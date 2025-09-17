import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Wish, Tag

User = get_user_model()


class WishForm(forms.ModelForm):
    """
    A form for creating and updating a Wish object.
    It includes a custom tags_input field to handle comma-separated tags.
    """
    tags_input = forms.CharField(
        required=False,
        label="Tags",
        help_text="Enter tags separated by commas (e.g., 'books, electronics')"
    )

    class Meta:
        model = Wish
        fields = ['title', 'image', 'price', 'shop_link', 'description', 'private', 'completed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure that the price field is not set to required to allow wishes without a price
        self.fields['price'].required = False
        # If an instance exists (for editing), populate the tags_input field
        if self.instance.pk:
            current_tags = ", ".join([tag.name for tag in self.instance.tags.all()])
            self.fields['tags_input'].initial = current_tags

    def save(self, commit=True):
        """
        Custom save method to handle saving the Wish instance and its ManyToMany tags relationship.
        """
        wish = super().save(commit=False)
        if commit:
            wish.save()
            self._save_tags(wish)
        return wish

    def _save_tags(self, wish_instance):
        """
        Helper method to process and save tags from the tags_input field.
        """
        tags_data = self.cleaned_data.get('tags_input')
        # Clear existing tags first to prevent duplicates or orphaned tags
        wish_instance.tags.clear()

        if tags_data:
            tag_names = [tag.strip() for tag in tags_data.split(',') if tag.strip()]

            for tag_name in tag_names:
                # Get or create the tag globally
                tag, created = Tag.objects.get_or_create(name=tag_name)
                wish_instance.tags.add(tag)


class ProfileForm(forms.ModelForm):
    """
    A form for updating the user's profile information.
    This form is specifically for updating the username.
    """

    class Meta:
        model = User
        fields = ['username']

    def clean_username(self):
        """
        Custom validator for the username field to restrict allowed characters.
        """
        username = self.cleaned_data['username']
        # Regex allows only Latin letters, numbers, dashes, or underscores.
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError("Username must contain only Latin letters, numbers, dashes, or underscores.")
        return username
