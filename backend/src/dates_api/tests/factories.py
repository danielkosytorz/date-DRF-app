from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger, FuzzyText

from src.dates_api.models import Date


class DateFactory(DjangoModelFactory):
    class Meta:
        model = Date

    month = FuzzyInteger(1, 12)
    day = FuzzyInteger(1, 31)
    fact = FuzzyText(length=100)
