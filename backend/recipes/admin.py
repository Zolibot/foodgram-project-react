from django.contrib import admin
from .models import Ingredient, Tag, Recipes, IngredientAmount, FavoriteRecipes


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'cooking_time')
    list_filter = ('cooking_time', 'pub_date')


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
