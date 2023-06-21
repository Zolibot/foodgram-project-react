from rest_framework import serializers

from users.models import User, Follow


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для user"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, obj):
        """Проверка подписки юзера на автора."""
        user = self.context.get('request').user.id
        if user is None:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()
