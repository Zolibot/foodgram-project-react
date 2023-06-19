from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User, Follow


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для user"""

    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(regex='^[\w.@+-]+\Z'),
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        """Проверка подписки юзера на автора."""
        user = self.context.get('request').user.id
        if user is None:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
