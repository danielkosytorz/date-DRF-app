from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Date(models.Model):
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    fact = models.CharField(max_length=300)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["month", "day"], name="Unique day and month"
            )
        ]


class PopularMonth(models.Model):
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], unique=True
    )
    days_checked = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(31)]
    )
