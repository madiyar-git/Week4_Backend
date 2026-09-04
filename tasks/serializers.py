from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Task, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "owner", "created_at"]
        read_only_fields = ["id", "created_at", "owner"]


class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    owner = serializers.ReadOnlyField(source="owner.username")
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=False
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "priority",
            "category",
            "category_id",
            "created_at",
            "updated_at",
            "owner",
            "tags",
        ]
        read_only_fields = ["owner", "id", "created_at", "updated_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tags"] = TagSerializer(instance.tags.all(), many=True).data
        return representation

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters")
        return value.strip()

    priority = serializers.SerializerMethodField()

    @extend_schema_field(str)
    def get_priority(self, obj) -> str:
        mapping = {1: "low", 2: "medium", 3: "high"}
        return mapping.get(obj.priority, "medium")

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)

        if "priority" in data:
            priority_word = data["priority"]
            word_to_num = {"low": 1, "medium": 2, "high": 3}

            if priority_word in word_to_num:
                internal_data["priority"] = word_to_num[priority_word]
            else:
                raise serializers.ValidationError(
                    {
                        "priority": "Invalid priority level. Must be 'low', 'medium', or 'high'."
                    }
                )

        return internal_data
