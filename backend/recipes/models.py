from django.db import models
from django.core.validators import RegexValidator
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
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


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
        validators=[
            RegexValidator(
                regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$'
            )
        ],
    )
    slug = models.SlugField(
        'Slug',
        max_length=100,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$'
            )
        ],
    )

    class Meta:
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
        null=False,
        blank=False,
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Название рецепта',
        max_length=250,
        null=False,
        blank=False,
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Фото',
        help_text='Фото рецепта',
        upload_to='food/',
        null=False,
        blank=False,
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
        null=False,
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
    cooking_time = models.IntegerField(
        verbose_name='Время',
        help_text='Время приготовления в минутах',
        null=False,
        blank=False,
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
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество ингредиента',
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            )
        ]
