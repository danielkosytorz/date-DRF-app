import requests
from django.db.models import Count
from django.db.models.query import QuerySet

from src.dates_api.exceptions import NumbersAPIErrorException
from src.dates_api.models import Date, PopularMonth


class DateService:
    NUMBERS_API_BASE_URL = "http://numbersapi.com/"

    @classmethod
    def create_date(cls, month: int, day: int) -> Date:
        response = requests.get(url=f"{cls.NUMBERS_API_BASE_URL}{month}/{day}/date")
        if not response.ok:
            raise NumbersAPIErrorException

        if (date := Date.objects.filter(month=month, day=day).first()) is not None:
            date = cls.update_date_fact(date=date, fact=response.text)
            return date

        return Date.objects.create(month=month, day=day, fact=response.text)

    @staticmethod
    def update_date_fact(date: Date, fact: str) -> Date:
        date.fact = fact
        date.save()
        return date

    @staticmethod
    def get_ranking_of_months() -> QuerySet:
        return Date.objects.values("month").annotate(days_checked=Count("day"))

    @staticmethod
    def get_month_name_from_number(month: int) -> str:
        return {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }.get(month)

    @classmethod
    def create_or_update_popular_months(cls) -> None:
        for month in cls.get_ranking_of_months():
            PopularMonth.objects.update_or_create(
                month=month.get("month"),
                defaults={"days_checked": month.get("days_checked")},
            )
