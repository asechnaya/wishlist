# wishes/forms.py

from django import forms
from .models import Wish, Tag


class WishForm(forms.ModelForm):
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

        if self.instance.pk:
            current_tags = ", ".join([tag.name for tag in self.instance.tags.all()])
            self.fields['tags_input'].initial = current_tags

    def save(self, commit=True):
        wish = super().save(commit=False)
        if commit:
            wish.save()
            self._save_tags(wish)
        return wish

    def _save_tags(self, wish_instance):
        tags_data = self.cleaned_data.get('tags_input')

        wish_instance.tags.clear()

        if tags_data:
            tag_names = [tag.strip() for tag in tags_data.split(',') if tag.strip()]

            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                wish_instance.tags.add(tag)