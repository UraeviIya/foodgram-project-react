import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

# /home/evgenius/Documents/Ya.practicum/python_developer/dev2/fgp-react/foodgram-project-react/backend/foodgram/static/data
# FILE2IMPORT = os.path.join(settings.STATICFILES_DIRS[0], 'data/users.csv')

# FILE2IMPORT = os.path.join(settings.BASE_DIR,'/static/data/ingredients.csv')
FILE2IMPORT = os.path.join(settings.DATAFILES_DIRS[0], 'data/ingredients.csv')


class Command(BaseCommand):
    help = 'load ingredients from csv. data folder must be placed in static.'

    def handle(self, *args, **options):
        with open(FILE2IMPORT, encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                # print(row)
                name = row['name']
                measurement_unit = row['measurement_unit']
                ingredients = Ingredient(
                    name=name,
                    measurement_unit=measurement_unit
                )
                ingredients.save()
