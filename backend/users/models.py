from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    USER = 'user'
    ADMIN = 'admin'


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        max_length=254,
        choices=Role.choices,
        default=Role.USER,
        blank=True,
        verbose_name='Тип учётной записи',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'following'], name='follow_user'
        )
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'
