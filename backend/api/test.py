from django.contrib.auth import get_user_model
from django.test import TestCase
from recipes.models import Tag, Recipes, IngredientAmount, Ingredient
from rest_framework import status
from rest_framework.test import APIClient


class FoodgramAPITestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='auth_user',
            email='ururu@utu.ru',
            first_name='Alex',
            last_name='sadasd',
            password='Qwerty123123',
        )
        self.user2 = User.objects.create_user(
            username='auth_user2',
            email='ururu2@utu.ru',
            first_name='Alex2',
            last_name='sadasd2',
            password='Qwerty123123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.non_client = APIClient()
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

    def test_users(self):
        response = self.client.get('/api/users/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            'авторизованый пользователь не может получить доступ',
        )

        response = self.non_client.get('/api/users/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            'неавторизованый пользователь не может получить доступ',
        )

        data = {
            'email': 'vpupkin2@yandex.ru',
            'username': 'vasya2.pupkin',
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'password': 'Qwerty123123',
        }

        response = self.non_client.post(
            '/api/users/', data=data, format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            'не создает пользователя',
        )

        data = {
            'email': 'vpupkin@yandex.ru',
            'username': 'vasya.pupkin',
            'last_name': 'Пупкин',
            'password': 'Qwerty123123',
        }

        response = self.non_client.post(
            '/api/users/', data=data, format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            'Должна быть ошибка',
        )

        response = self.non_client.get('/api/users/1/')
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            'У не авторизованого нет доспупа',
        )

        response = self.client.get('/api/users/1/')
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, 'Есть доступ'
        )

        response = self.client.get('/api/users/5/')
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            'Обьекта не должно быть',
        )

        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.non_client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
            "new_password": ",pasdmkoasd12",
            "current_password": "Qwerty123123",
        }

        response = self.client.post(
            '/api/users/set_password/', data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        data = {
            "new_password": "12345",
            "current_password": ",pasdmkoasd12",
        }

        response = self.client.post(
            '/api/users/set_password/', data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "new_password": ",pasdmkoasd12",
            "current_password": "Qwerty123123",
        }

        response = self.non_client.post(
            '/api/users/set_password/', data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {"password": ",pasdmkoasd12", "email": "ururu@utu.ru"}

        response = self.client.post(
            '/api/auth/token/login/', data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/auth/token/logout/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.non_client.post('/api/auth/token/logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tags(self):
        tag = Tag.objects.create(
            name='Завтрак',
            color='#ffffff',
            slug='breakfast',
        )
        tag.save()

        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.non_client.get('/api/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/tags/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.non_client.get('/api/tags/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/tags/3/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.non_client.get('/api/tags/3/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_request(self):
        ingredient = Ingredient.objects.create(
            name='трава',
            measurement_unit='кг',
        )
        ingredient.save()

        data_recipe = {
            "ingredients": [{"id": 1, "amount": 10}],
            "tags": [],
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "string",
            "text": "string",
            "cooking_time": 1,
        }

        response = self.client.post(
            '/api/recipes/', data=data_recipe, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/recipes/1/shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/recipes/1/shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.non_client.post('/api/recipes/1/shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete('/api/recipes/1/shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete('/api/recipes/1/shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/api/recipes/1/shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.non_client.delete('/api/recipes/1/shopping_cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        urls = [
            '/api/recipes/',
            '/api/recipes/1/',
            '/api/recipes/download_shopping_cart/',
            '/api/ingredients/',
            '/api/ingredients/1/',
        ]

        for url in urls:
            response = self.client.get(url)
            with self.subTest(f'ответ должен быть 200 {url}'):
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        data_recipe = {
            "ingredients": [{"id": 1, "amount": 10}],
            "tags": [],
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "stringqweqwe",
            "cooking_time": 1,
        }

        response = self.client.patch(
            '/api/recipes/1/', data=data_recipe, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.non_client.patch(
            '/api/recipes/1/', data=data_recipe, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client2.patch(
            '/api/recipes/1/', data=data_recipe, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data_recipe = {
            "ingredients": [{"id": 1, "amount": 10}],
            "tags": [],
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "stringqweqwe",
            "cooking_time": 0,
        }

        response = self.client.patch(
            '/api/recipes/1/', data=data_recipe, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client2.delete('/api/recipes/1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.non_client.delete('/api/recipes/1/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete('/api/recipes/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete('/api/recipes/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorite(self):
        response = self.client.get('/api/users/subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.non_client.get('/api/users/subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post('/api/users/2/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/api/users/2/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/api/users/1/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.non_client.post('/api/users/2/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post('/api/users/22/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete('/api/users/2/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete('/api/users/2/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.non_client.delete('/api/users/2/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete('/api/users/22/subscribe/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ingidients(self):
        ingredient = Ingredient.objects.create(
            name='трава',
            measurement_unit='кг',
        )
        ingredient.save()
        response = self.client.get('/api/ingredients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/ingredients/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.non_client.get('/api/ingredients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.non_client.get('/api/ingredients/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
