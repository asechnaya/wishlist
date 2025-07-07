# wishes/models.py

from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
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
    private = models.BooleanField(default=False)
    # NEW FIELD: Boolean field to indicate if a wish is completed
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        # Order by completed status (False first, then True), then by creation date
        ordering = ['completed', '-created_at']
