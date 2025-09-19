import os
import re
from urllib.parse import urlsplit
from urllib.request import urlopen

from django import forms
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from .models import Wish, Tag

User = get_user_model()


class WishForm(forms.ModelForm):
    """
    A form for creating and updating a Wish object.
    It includes a custom tags_input field to handle comma-separated tags.
    """
    image_file = forms.ImageField(required=False, label="Image (upload)")
    image_url = forms.URLField(required=False, label="Image URL", help_text="Direct link to image (jpg, png, gif)")

    tags_input = forms.CharField(
        required=False,
        label="Tags",
        help_text="Enter tags separated by commas (e.g., 'books, electronics')"
    )

    class Meta:
        model = Wish
        fields = ['title', 'price', 'shop_link', 'description', 'private', 'completed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow wishes without a price
        self.fields['price'].required = False
        # If an instance exists (for editing), populate the tags_input field
        if self.instance.pk:
            current_tags = ", ".join(tag.name for tag in self.instance.tags.all())
            self.fields['tags_input'].initial = current_tags

    def clean(self):
        cleaned = super().clean()
        image_file = cleaned.get("image_file")
        image_url = cleaned.get("image_url")

        if image_file and image_url:
            raise forms.ValidationError("Choose only one option: either upload or URL.")

        if image_url:
            path = urlsplit(image_url).path.lower()
            if not any(path.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
                self.add_error("image_url", "It seems this is not a direct link to the image.")

        return cleaned

    def save(self, commit=True):
        """
        Save the Wish instance, handle image source (upload or URL),
        and persist tags from the tags_input field.
        """
        instance = super().save(commit=False)
        image_file = self.cleaned_data.get("image_file")
        image_url = self.cleaned_data.get("image_url")

        if image_file:
            instance.image = image_file
        elif image_url:
            try:
                with urlopen(image_url, timeout=5) as resp:
                    data = resp.read()
                    url_path = urlsplit(image_url).path
                    base_name = os.path.basename(url_path) or "image"
                    if "." not in base_name:
                        # Infer extension from content-type when URL path has no extension
                        get_ct = getattr(resp.headers, "get_content_type", None)
                        content_type = get_ct() if callable(get_ct) else resp.headers.get("Content-Type", "")
                        ext_map = {
                            "image/jpeg": ".jpg",
                            "image/png": ".png",
                            "image/gif": ".gif",
                            "image/webp": ".webp",
                        }
                        base_name += ext_map.get(content_type, ".jpg")
                    instance.image.save(base_name, ContentFile(data), save=False)
            except Exception:
                # If fetching fails, skip attaching the image; clean() already validates URL format.
                pass

        def _save_m2m():
            # Preserve default M2M behavior (if any) and then handle tags_input
            forms.ModelForm.save_m2m(self)
            self._save_tags(instance)

        if commit:
            instance.save()
            _save_m2m()
        else:
            # Defer M2M/tag saving until the caller invokes form.save_m2m()
            self.save_m2m = _save_m2m

        return instance

    def _save_tags(self, wish_instance):
        """
        Helper to process and save tags from the tags_input field.
        Clears existing tags and re-attaches based on current input.
        """
        tags_data = self.cleaned_data.get('tags_input', '')
        # Clear existing tags to prevent duplicates or orphaned tags
        wish_instance.tags.clear()

        if tags_data:
            tag_names = [tag.strip() for tag in tags_data.split(',') if tag.strip()]
            tags = []
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            if tags:
                wish_instance.tags.add(*tags)


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