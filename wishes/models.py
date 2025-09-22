# wishes/models.py

from django.db import models
from django.contrib.auth.models import User
from djmoney.models.fields import MoneyField

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
    price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD',
        null=True,
        blank=True,
    )

    shop_link = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def is_public(self) -> bool:
        return not self.private


    class Meta:
        ordering = ['completed', '-created_at']
