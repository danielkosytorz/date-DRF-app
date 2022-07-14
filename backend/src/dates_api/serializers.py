from rest_framework import serializers

from src.dates_api.models import Date, PopularMonth
from src.dates_api.services import DateService


class DateOutputSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = Date
        fields = ("id", "month", "day", "fact")

    def get_month(self, obj: Date) -> str:
        return DateService.get_month_name_from_number(month=obj.month)


class DateInputSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12)
    day = serializers.IntegerField(min_value=1, max_value=31)

    def validate(self, attrs):
        month = attrs.get("month")
        day = attrs.get("day")
        days_in_months = {
            1: 31,
            2: 29,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31,
        }
        if day > days_in_months.get(month):
            raise serializers.ValidationError(
                f"Day {day} is not valid for month {month}"
            )
        return attrs


class PopularMonthOutputSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()

    class Meta:
        model = PopularMonth
        fields = ("id", "month", "days_checked")

    def get_month(self, obj: Date) -> str:
        return DateService.get_month_name_from_number(month=obj.month)
