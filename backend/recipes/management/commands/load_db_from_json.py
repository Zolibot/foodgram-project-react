import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загрузка данных из "data/ingredients.json и data/tags.json"'

    def handle(self, *args, **options):
        data_folder = Path('data/')
        file_path = {
            str(p.name).rstrip('.json'): p for p in data_folder.iterdir()
        }
        load_same_model = {
            'ingredient': Ingredient,
            'tag': Tag,
        }
        try:
            for name, model in load_same_model.items():
                print('Модель', name)
                self.load_data(file_path[name], model)
            print('Данные успешно импортированы в БД')
        except Exception as r:
            raise CommandError('Ошибка загрузки данных', r)

    def load_data(self, path, model):
        with open(path) as file:
            data = json.load(file)
            instances = tqdm(data, ncols=80)
            temp_instances = []
            for instance in instances:
                instances.set_description(
                    f"Загрузка - '{instance['name'][:5]}'"
                )
                temp_instances.append(model(**instance))
            model.objects.bulk_create(temp_instances)
