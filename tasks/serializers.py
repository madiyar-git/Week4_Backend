from rest_framework import serializers
from .models import Task, Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True,
    )
    owner = serializers.ReadOnlyField(source='owner.username')
    # TODO что такое ОРМ DJANGO и как относится к сериалайзеру
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed',
            'priority', 'category', 'category_id',
            'created_at', 'updated_at', 'owner'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters")
        return value

    priority = serializers.SerializerMethodField()

    def get_priority(self, obj):
        mapping = {1: 'low', 2: 'medium', 3: 'high'}
        return mapping.get(obj.priority, 'medium')

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)

        if 'priority' in data:
            priority_word = data['priority']
            word_to_num = {'low': 1, 'medium': 2, 'high': 3}

            if priority_word in word_to_num:
                internal_data['priority'] = word_to_num[priority_word]

        return internal_data