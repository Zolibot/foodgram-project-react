from django.contrib import admin

from recipes.models import (
    FavoriteRecipes,
    Ingredient,
    IngredientAmount,
    Recipes,
    ShoppingCart,
    Tag,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    min_num = 1


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name',)
    filter_horizontal = ('ingredients', 'tags')
    inlines = [IngredientAmountInline]

    @admin.display(description='Количество в избранном')
    def count(self, recipe):
        return FavoriteRecipes.objects.filter(recipe=recipe).count()


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
