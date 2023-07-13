from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomTokenCreateView,
    IngredientViewSet,
    RecipesViewSet,
    TagViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', CustomTokenCreateView.as_view(), name='login'),
    path('auth/', include('djoser.urls.authtoken')),
]
