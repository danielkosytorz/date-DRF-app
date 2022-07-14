import random
from typing import Optional
from unittest.mock import patch

from decouple import config
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from src.dates_api.models import Date, PopularMonth
from src.dates_api.services import DateService
from src.dates_api.tests.factories import DateFactory


class DatesViewSetTestCase(APITestCase):
    class MockResponse:
        def __init__(self, status_code: int, text: Optional[str] = None):
            self.status_code = status_code
            self.text = text

        @property
        def ok(self):
            return True if self.status_code < 400 else False

    @classmethod
    def setUpTestData(cls):
        cls.x_api_key = config("X_API_KEY")
        cls.dates_list_url = reverse("dates_api:dates-list")
        cls.create_date_valid_data = {
            "month": 1,
            "day": 1,
        }
        cls.create_date_invalid_data = {
            "month": 13,
            "day": 32,
        }
        cls.create_date_invalid_days_in_month = {
            "month": 2,
            "day": 30,
        }

    @patch("src.dates_api.services.requests.get")
    def test_create_date_with_valid_data(self, mock_requests_get):
        mock_requests_get.return_value = self.MockResponse(
            status_code=200,
            text="January 1st is the day in 1502 that the present-day location of Rio de Janeiro is first explored by the Portuguese.",
        )
        response = self.client.post(
            path=self.dates_list_url, data=self.create_date_valid_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Date.objects.count(), 1)
        new_date = Date.objects.first()
        self.assertEqual(
            response.data,
            {
                "id": new_date.id,
                "month": DateService.get_month_name_from_number(month=new_date.month),
                "day": new_date.day,
                "fact": new_date.fact,
            },
        )

    @patch("src.dates_api.services.requests.get")
    def test_create_date_raise_NumbersAPIErrorException(self, mock_requests_get):
        mock_requests_get.return_value = self.MockResponse(status_code=400)

        response = self.client.post(
            path=self.dates_list_url, data=self.create_date_valid_data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Date.objects.count(), 0)
        self.assertEqual(response.data.get("detail"), "Numbers API error.")

    def test_create_date_with_invalid_data(self):
        response = self.client.post(
            path=self.dates_list_url, data=self.create_date_invalid_data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("month")[0],
            "Ensure this value is less than or equal to 12.",
        )
        self.assertEqual(Date.objects.count(), 0)

    def test_create_date_with_invalid_days_in_month(self):
        response = self.client.post(
            path=self.dates_list_url, data=self.create_date_invalid_days_in_month
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("non_field_errors")[0],
            f"Day {self.create_date_invalid_days_in_month.get('day')} is not valid for month {self.create_date_invalid_days_in_month.get('month')}",
        )
        self.assertEqual(Date.objects.count(), 0)

    @patch("src.dates_api.services.requests.get")
    def test_create_date_for_already_existing_day_and_month(self, mock_requests_get):
        date = DateFactory()
        new_fact = "January 1st is the day in 1502 that the present-day location of Rio de Janeiro is first explored by the Portuguese."
        mock_requests_get.return_value = self.MockResponse(
            status_code=200,
            text=new_fact,
        )

        response = self.client.post(
            path=self.dates_list_url, data={"month": date.month, "day": date.day}
        )
        date.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Date.objects.count(), 1)
        self.assertEqual(
            response.data,
            {
                "id": date.id,
                "month": DateService.get_month_name_from_number(month=date.month),
                "day": date.day,
                "fact": new_fact,
            },
        )

    def test_delete_date_without_XAPIKEY(self):
        date = DateFactory()
        response = self.client.delete(
            path=reverse("dates_api:dates-detail", kwargs={"pk": date.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Date.objects.count(), 1)

    def test_delete_date_with_valid_id(self):
        date = DateFactory()
        response = self.client.delete(
            path=reverse("dates_api:dates-detail", kwargs={"pk": date.id}),
            **{"HTTP_X-API-KEY": self.x_api_key},
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Date.objects.count(), 0)

    def test_delete_date_invalid_id(self):
        DateFactory()
        response = self.client.delete(
            path=reverse("dates_api:dates-detail", kwargs={"pk": 99}),
            **{"HTTP_X-API-KEY": self.x_api_key},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Date.objects.count(), 1)

    def test_get_list_of_dates(self):
        date_1 = DateFactory()
        date_2 = DateFactory()
        response = self.client.get(path=self.dates_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Date.objects.count(), 2)
        self.assertEqual(
            response.data,
            [
                {
                    "id": date_1.id,
                    "month": DateService.get_month_name_from_number(date_1.month),
                    "day": date_1.day,
                    "fact": date_1.fact,
                },
                {
                    "id": date_2.id,
                    "month": DateService.get_month_name_from_number(date_2.month),
                    "day": date_2.day,
                    "fact": date_2.fact,
                },
            ],
        )


class PopularMonthListViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dates_list_url = reverse("dates_api:popular_month")
        cls.dates = [
            DateFactory(month=i, day=j)
            for i in range(1, 13)
            for j in range(1, random.randint(2, 10))
        ]

    def test_get_list_of_popular_months(self):
        response = self.client.get(path=self.dates_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "id": popular_month.id,
                    "month": DateService.get_month_name_from_number(
                        month=popular_month.month
                    ),
                    "days_checked": popular_month.days_checked,
                }
                for popular_month in PopularMonth.objects.order_by("-days_checked")
            ],
        )
