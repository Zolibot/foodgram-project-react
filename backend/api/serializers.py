from rest_framework import serializers
from django.core.files.base import ContentFile
import base64

from users.models import User, Follow
from recipes.models import (
    Tag,
    Ingredient,
    Recipes,
    IngredientAmount,
    FavoriteRecipes,
    ShoppingCart
)


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

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, following=obj).exists()


class FollowSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='following.id')
    email = serializers.ReadOnlyField(source='following.email')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.following).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = Recipes.objects.filter(author=obj.following)
        if 'recipes_limit' in request.query_params:
            queryset = queryset[:int(request.query_params['recipes_limit'])]
        serializer = FavoriteSerializer(
            queryset, many=True, context={'request': request})
        return serializer.data

    def get_is_subscribed(self, obj):
        """Проверка подписки юзера на автора."""
        return Follow.objects.filter(
            user=obj.user, following=obj.following).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsAmountSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    ingredients = IngredientsAmountSerializer(
        many=True, source='recipe'
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user, recipe=obj).exists()


class IngredientsAmountCreateSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'amount',
        )


class RecipesCreateSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientsAmountCreateSerializer(
        many=True, source='recipe'
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def update_or_create_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.update_or_create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount'],
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe')
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.update_or_create_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        ingredients = validated_data.pop('recipe')
        instance.ingredients.clear()
        self.update_or_create_ingredient(ingredients, instance)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.HyperlinkedModelSerializer):

    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
