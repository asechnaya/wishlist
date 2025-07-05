# wishes/models.py

from django.db import models
from django.contrib.auth.models import User


# Removed: from django.db.models import UniqueConstraint # This line should NOT be here

class Tag(models.Model):
    # Removed unique=True from name, as uniqueness will now be per user
    name = models.CharField(max_length=50)

    class Meta:
        # Optional: Order tags alphabetically by name
        ordering = ['name']

    def __str__(self):
        # This should be present for global tags:
        return self.name


class Wish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishes')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='wish_avatars/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shop_link = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
