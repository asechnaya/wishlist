from django import forms
from .models import Wish, Tag


class WishForm(forms.ModelForm):
    # Change 'tags' to a CharField for input, but handle the M2M relationship manually.
    # We will process this string into Tag objects.
    tags_input = forms.CharField(
        required=False,
        label="Tags",  # User-friendly label
        help_text="Enter tags separated by commas (e.g., 'books, electronics')"
    )

    class Meta:
        model = Wish
        fields = ['title', 'image', 'price', 'shop_link', 'description']  # Remove 'tags' from here

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing wish, populate the tags_input field
        if self.instance.pk:
            current_tags = ", ".join([tag.name for tag in self.instance.tags.all()])
            self.fields['tags_input'].initial = current_tags

    def save(self, commit=True):
        # Save the Wish instance first
        wish = super().save(commit=False)
        if commit:
            wish.save()
            # Now handle the tags_input field to update the ManyToMany relationship
            self._save_tags(wish)
        return wish

    def _save_tags(self, wish_instance):
        # Get the cleaned data from the custom tags_input field
        tags_data = self.cleaned_data.get('tags_input')

        # Clear existing tags to prevent duplicates if editing
        wish_instance.tags.clear()

        if tags_data:
            # Split the string by commas and strip whitespace from each tag name
            tag_names = [tag.strip() for tag in tags_data.split(',') if tag.strip()]

            for tag_name in tag_names:
                # Get or create the Tag object
                tag, created = Tag.objects.get_or_create(name=tag_name)
                # Add the Tag object to the Wish instance's tags
                wish_instance.tags.add(tag)
