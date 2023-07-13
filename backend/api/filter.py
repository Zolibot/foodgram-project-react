from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    BooleanFilter,
    ModelMultipleChoiceFilter,
)

from recipes.models import Recipes, Tag


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(field_name='is_favorited', method='favorited')
    is_in_shopping_cart = BooleanFilter(
        field_name='is_in_shopping_cart', method='in_shopping_cart'
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    def favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value:
            return queryset.filter(favorite_recipes__user=user)
        return queryset.exclude(favorite_recipes__user=user)

    def in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value:
            return queryset.filter(shopping_recipes__user=user)
        return queryset.exclude(shopping_recipes__user=user)

    class Meta:
        model = Recipes
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
