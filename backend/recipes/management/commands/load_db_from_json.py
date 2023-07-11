import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

from tqdm import tqdm
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингридиентов из "../data/ingredients.json"'

    def handle(self, *args, **options):
        file_path = Path('../data/ingredients.json')
        try:
            self.load_ingredients(file_path)
            print('Данные успешно импортированы в БД')
        except Exception as r:
            raise CommandError('Ошибка загрузки данных', r)

    def load_ingredients(self, path):
        with open(path) as file:
            data = json.load(file)
            ingredients = tqdm(data, ncols=80)
            temp_instances = []
            for ingredient in ingredients:
                ingredients.set_description(
                    f"Загрузка '{ingredient['name'][:5]}'"
                )
                temp_instances.append(Ingredient(**ingredient))
            Ingredient.objects.bulk_create(temp_instances)
