from django.http import FileResponse
from tabulate import tabulate


def get_shopping_ingredient(ingredients):
    head = ["No.", "Наименование", "Количество", "Ед.изм."]
    data = []
    for count, ingredient in enumerate(ingredients, start=1):
        data.append(
            [
                str(count),
                ingredient['ingredient__name'],
                str(ingredient['amount_sum']),
                ingredient['ingredient__measurement_unit'],
            ]
        )

    table = tabulate(data, headers=head, tablefmt="github")
    return FileResponse(
        table,
        content_type='text/plain',
        as_attachment=True,
        filename="shopping_cart.txt",
    )
