# wishes/serializers.py
from rest_framework import serializers
from .models import Wish, Tag, User # Import User model

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class WishSerializer(serializers.ModelSerializer):
    # Use nested serializers to include related data
    user = UserSerializer(read_only=True) # Read-only for user, as it's assigned by backend
    tags = TagSerializer(many=True, read_only=True) # Read-only for tags, as they are managed via tags_input

    # Add a write-only field for tags input (comma-separated string)
    tags_input = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Wish
        fields = [
            'id', 'user', 'title', 'image', 'price', 'shop_link',
            'description', 'created_at', 'private', 'completed', 'tags', 'tags_input'
        ]
        read_only_fields = ['created_at'] # created_at is automatically set

    def create(self, validated_data):
        tags_input_data = validated_data.pop('tags_input', '')
        wish = Wish.objects.create(**validated_data)
        self._handle_tags(wish, tags_input_data)
        return wish

    def update(self, instance, validated_data):
        tags_input_data = validated_data.pop('tags_input', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle tags update if tags_input was provided
        if tags_input_data is not None:
            self._handle_tags(instance, tags_input_data)
        return instance

    def _handle_tags(self, wish_instance, tags_input_data):
        wish_instance.tags.clear() # Clear existing tags
        if tags_input_data:
            tag_names = [tag.strip() for tag in tags_input_data.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                wish_instance.tags.add(tag)

