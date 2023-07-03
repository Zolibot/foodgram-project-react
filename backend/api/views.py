from djoser.views import UserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from users.models import User, Follow
from recipes.models import Ingredient, Recipes, Tag
from .permissions import IsAuthorOrReadOnly

from .serializers import (
    IngredientSerializer,
    RecipesSerializer,
    TagSerializer,
    UserSerializer,
    RecipesCreateSerializer,
    FollowSerializer
)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    pagination_class = PageNumberPagination

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
        pagination_class=LimitOffsetPagination
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class MultiSerializerViewSet(ModelViewSet):
    serializers = {
        'default': None,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action)


class RecipesViewSet(MultiSerializerViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'id'
    serializers = {
        'list': RecipesSerializer,
        'detail': RecipesSerializer,
        'retrieve': RecipesSerializer,
        'create': RecipesCreateSerializer,
        'update': RecipesCreateSerializer,
        'partial_update': RecipesCreateSerializer,
    }
