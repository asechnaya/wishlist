# wishes/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint  # Import UniqueConstraint for combined unique fields


class Tag(models.Model):
    # NEW: Link Tag to a specific User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tags')
    # Removed unique=True from name, as uniqueness will now be per user
    name = models.CharField(max_length=50)

    class Meta:
        # NEW: Add a unique constraint to ensure that a user cannot have
        # two tags with the exact same name. Different users can have tags
        # with the same name.
        constraints = [
            UniqueConstraint(fields=['user', 'name'], name='unique_user_tag')
        ]
        # Optional: Order tags alphabetically by name
        ordering = ['name']

    def __str__(self):
        # Include the user's username for clarity in admin or debugging
        return f"{self.name} (by {self.user.username})"


class Wish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishes')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='wish_avatars/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shop_link = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # The ManyToManyField remains the same, as it links to the Tag model
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
