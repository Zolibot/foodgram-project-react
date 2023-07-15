from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингридиент',
        help_text='Наименование ингридиента',
        max_length=150,
        db_index=True,
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Единица измерения количества ингредиента',
        max_length=150,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        help_text='Наименование тега',
        max_length=150,
        db_index=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        help_text='Цвет в НЕХ формате',
        max_length=8,
        validators=[RegexValidator(regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$')],
    )
    slug = models.SlugField(
        'Slug',
        max_length=100,
        unique=True,
        db_index=True,
        validators=[RegexValidator(regex=r'^[-a-zA-Z0-9_]+$')],
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False,
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Название рецепта',
        max_length=200,
        blank=False,
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Фото',
        help_text='Фото рецепта',
        upload_to='food/',
        blank=False,
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Теги рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        help_text='Ингридиенты для рецепта',
        through='IngredientAmount',
        blank=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время',
        help_text='Время приготовления в минутах',
        blank=False,
        validators=[
            MinValueValidator(settings.MIN_VALUE),
            MaxValueValidator(settings.MAX_VALUE),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество ингредиента',
        validators=[
            MinValueValidator(settings.MIN_VALUE),
            MaxValueValidator(settings.MAX_VALUE),
        ],
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return self.ingredient


class FavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Рецепты',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_recipe',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное  - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopping_recipes',
        verbose_name='Рецепты',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_recipe',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в список покупок - {self.recipe}'
