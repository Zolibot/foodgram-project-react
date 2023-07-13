import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import (
    ImageField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
)
from recipes.models import (
    FavoriteRecipes,
    Ingredient,
    IngredientAmount,
    Recipes,
    ShoppingCart,
    Tag,
)
from users.models import User, Follow


class UserSerializer(ModelSerializer):
    """Сериализатор для user"""

    is_subscribed = SerializerMethodField(read_only=True)

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


class FollowSerializer(ModelSerializer):
    id = ReadOnlyField(source='following.id')
    email = ReadOnlyField(source='following.email')
    username = ReadOnlyField(source='following.username')
    first_name = ReadOnlyField(source='following.first_name')
    last_name = ReadOnlyField(source='following.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

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
            queryset = queryset[: int(request.query_params['recipes_limit'])]
        serializer = FavoriteSerializer(
            queryset, many=True, context={'request': request}
        )
        return serializer.data

    def get_is_subscribed(self, obj):
        """Проверка подписки юзера на автора."""
        return Follow.objects.filter(
            user=obj.user, following=obj.following
        ).exists()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsAmountSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipesSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientsAmountSerializer(many=True, source='recipe')
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

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
        return FavoriteRecipes.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class IngredientsAmountCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'amount',
        )


class RecipesCreateSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientsAmountCreateSerializer(many=True, source='recipe')
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


class FavoriteSerializer(ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = ReadOnlyField()
    cooking_time = ReadOnlyField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
