from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    USER = 'user'
    ADMIN = 'admin'


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=254,
        unique=True,
        null=False
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        verbose_name='Пользователь',
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False
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

    is_admin.fget.short_description = 'Админ'


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
        unique_together = ['user', 'following']
        models.UniqueConstraint(
            fields=['user', 'following'], name='follow_user'
        )
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'
