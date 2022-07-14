from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from src.dates_api.models import Date, PopularMonth
from src.dates_api.permissions import XAPIKEYPermission
from src.dates_api.serializers import (DateInputSerializer,
                                       DateOutputSerializer,
                                       PopularMonthOutputSerializer)
from src.dates_api.services import DateService


class DateViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Date.objects.all()
    serializer_class = DateOutputSerializer

    def get_permissions(self):
        self.permission_classes = (
            (AllowAny,) if self.action != "destroy" else (XAPIKEYPermission,)
        )
        return super().get_permissions()

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = DateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            data=self.get_serializer(
                DateService.create_date(
                    month=serializer.validated_data.get("month"),
                    day=serializer.validated_data.get("day"),
                )
            ).data,
            status=status.HTTP_201_CREATED,
        )


class PopularMonthListView(ListAPIView):
    serializer_class = PopularMonthOutputSerializer
    queryset = PopularMonth.objects.order_by("-days_checked")

    def list(self, request: Request, *args, **kwargs) -> Response:
        DateService.create_or_update_popular_months()
        return Response(
            self.get_serializer(self.get_queryset(), many=True).data,
            status=status.HTTP_200_OK,
        )
