from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet, TokenCreateView

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (
    FavoriteRecipes,
    Ingredient,
    IngredientAmount,
    Recipes,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User
from .filter import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipesCreateSerializer,
    RecipesSerializer,
    TagSerializer,
    UserSerializer,
)
from .utils import get_shopping_ingredient


class CustomTokenCreateView(TokenCreateView):

    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        pagination_class=None,
    )
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            if Follow.objects.filter(user=user, following=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'errors': 'Невозможно подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = FollowSerializer(
                Follow.objects.create(user=user, following=author),
                context={'request': request},
            )

            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if not Follow.objects.filter(user=user, following=author).exists():
            return Response(
                {'errors': 'Вы не были подписаны на автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(user=user, following=author).delete()
        return Response(
            'Вы успешно отписались от автора.',
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', None)
        if name:
            name = name.lower()
            queryset = queryset.filter(name__startswith=name)
        return queryset


class MultiSerializerViewSet(ModelViewSet):
    serializers = {
        'default': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action)


class RecipesViewSet(MultiSerializerViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    serializers = {
        'list': RecipesSerializer,
        'detail': RecipesSerializer,
        'retrieve': RecipesSerializer,
        'create': RecipesCreateSerializer,
        'update': RecipesCreateSerializer,
        'partial_update': RecipesCreateSerializer,
    }

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipes, pk=kwargs['id'])
        user = self.request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe, context={'request': request})
            if FavoriteRecipes.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже есть в избранном'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                FavoriteRecipes.objects.create(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if FavoriteRecipes.objects.filter(
                user=user, recipe=recipe
            ).exists():
                FavoriteRecipes.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Рецепт уже удален'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipes, pk=kwargs['id'])
        user = self.request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe, context={'request': request})
            if ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                return Response(
                    {'errors': 'Рецепт уже есть в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                ShoppingCart.objects.create(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Рецепт уже удален'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        pagination_class=None,
    )
    def download_shopping_cart(self, request, **kwargs):
        if not ShoppingCart.objects.filter(user=self.request.user).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_recipes__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount_sum=Sum('amount')
        ).order_by('ingredient__name')

        return get_shopping_ingredient(ingredients)
