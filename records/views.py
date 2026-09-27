from datetime import datetime, time

from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from inspections.models import (
    ATPReport,
    SanitationInspection,
)
from titrations.models import (
    SanitizerTitration,
    ChloragelTitration,
)

from .serializers import CombinedRecordSerializer


class CombinedRecordsAPIView(generics.ListAPIView):

    serializer_class = CombinedRecordSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        plant_id = request.query_params.get("plant")
        date_value = request.query_params.get("date")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        status_value = request.query_params.get("status")
        record_type = request.query_params.get("record_type")

        records = []

        # --------------------------------------------------
        # Sanitizer / Maxquat
        # --------------------------------------------------

        if not record_type or record_type == "sanitizer":

            sanitizer_queryset = SanitizerTitration.objects.select_related(
                "plant",
                "created_by",
            )

            if plant_id:
                sanitizer_queryset = sanitizer_queryset.filter(
                    plant_id=plant_id
                )

            if date_value:
                sanitizer_queryset = sanitizer_queryset.filter(
                    created_at__date=date_value
                )

            if start_date:
                sanitizer_queryset = sanitizer_queryset.filter(
                    created_at__date__gte=start_date
                )

            if end_date:
                sanitizer_queryset = sanitizer_queryset.filter(
                    created_at__date__lte=end_date
                )

            if status_value:
                sanitizer_queryset = sanitizer_queryset.filter(
                    status=status_value
                )

            for item in sanitizer_queryset:

                records.append(
                    {
                        "id": item.id,
                        "record_type": "sanitizer",
                        "plant": item.plant.id,
                        "plant_code": item.plant.code,
                        "plant_name": item.plant.name,
                        "status": item.status,
                        "date": item.created_at.date(),
                        "created_by": item.created_by.id,
                        "created_by_username": item.created_by.username,
                        "created_at": item.created_at,
                        "data": {
                            "r71_drops": item.r71_drops,
                            "sample_volume_ml": str(
                                item.sample_volume_ml
                            ),
                            "ppm": str(item.ppm),
                            "percent_vv": str(item.percent_vv),
                        },
                    }
                )

        # --------------------------------------------------
        # Chloragel
        # --------------------------------------------------

        if not record_type or record_type == "chloragel":

            chloragel_queryset = ChloragelTitration.objects.select_related(
                "plant",
                "created_by",
            )

            if plant_id:
                chloragel_queryset = chloragel_queryset.filter(
                    plant_id=plant_id
                )

            if date_value:
                chloragel_queryset = chloragel_queryset.filter(
                    created_at__date=date_value
                )

            if start_date:
                chloragel_queryset = chloragel_queryset.filter(
                    created_at__date__gte=start_date
                )

            if end_date:
                chloragel_queryset = chloragel_queryset.filter(
                    created_at__date__lte=end_date
                )

            if status_value:
                chloragel_queryset = chloragel_queryset.filter(
                    status=status_value
                )

            for item in chloragel_queryset:

                records.append(
                    {
                        "id": item.id,
                        "record_type": "chloragel",
                        "plant": item.plant.id,
                        "plant_code": item.plant.code,
                        "plant_name": item.plant.name,
                        "status": item.status,
                        "date": item.created_at.date(),
                        "created_by": item.created_by.id,
                        "created_by_username": item.created_by.username,
                        "created_at": item.created_at,
                        "data": {
                            "r9_drops": item.r9_drops,
                            "sample_volume_ml": str(
                                item.sample_volume_ml
                            ),
                            "result_percent": str(
                                item.result_percent
                            ),
                        },
                    }
                )

        # --------------------------------------------------
        # Sanitation Inspection
        # --------------------------------------------------

        if not record_type or record_type == "inspection":

            inspection_queryset = SanitationInspection.objects.select_related(
                "plant",
                "template",
                "inspector",
            )

            if plant_id:
                inspection_queryset = inspection_queryset.filter(
                    plant_id=plant_id
                )

            if date_value:
                inspection_queryset = inspection_queryset.filter(
                    inspection_date=date_value
                )

            if start_date:
                inspection_queryset = inspection_queryset.filter(
                    inspection_date__gte=start_date
                )

            if end_date:
                inspection_queryset = inspection_queryset.filter(
                    inspection_date__lte=end_date
                )

            if status_value:
                inspection_queryset = inspection_queryset.filter(
                    status=status_value
                )

            for item in inspection_queryset:

                records.append(
                    {
                        "id": item.id,
                        "record_type": "inspection",
                        "plant": item.plant.id,
                        "plant_code": item.plant.code,
                        "plant_name": item.plant.name,
                        "status": item.status,
                        "date": item.inspection_date,
                        "created_by": item.inspector.id,
                        "created_by_username": item.inspector.username,
                        "created_at": item.created_at,
                        "data": {
                            "template": item.template.name,
                            "general_notes": item.general_notes,
                            "signed_at": item.signed_at,
                        },
                    }
                )

        # --------------------------------------------------
        # ATP Reports
        # --------------------------------------------------

        if not record_type or record_type == "atp":

            atp_queryset = ATPReport.objects.select_related(
                "plant",
                "inspection",
                "uploaded_by",
            )

            if plant_id:
                atp_queryset = atp_queryset.filter(
                    plant_id=plant_id
                )

            if date_value:
                atp_queryset = atp_queryset.filter(
                    uploaded_at__date=date_value
                )

            if start_date:
                atp_queryset = atp_queryset.filter(
                    uploaded_at__date__gte=start_date
                )

            if end_date:
                atp_queryset = atp_queryset.filter(
                    uploaded_at__date__lte=end_date
                )

            if status_value:
                atp_queryset = atp_queryset.filter(
                    status=status_value
                )

            for item in atp_queryset:

                records.append(
                    {
                        "id": item.id,
                        "record_type": "atp",
                        "plant": item.plant.id,
                        "plant_code": item.plant.code,
                        "plant_name": item.plant.name,
                        "status": item.status,
                        "date": item.uploaded_at.date(),
                        "created_by": item.uploaded_by.id,
                        "created_by_username": item.uploaded_by.username,
                        "created_at": item.uploaded_at,
                        "data": {
                            "original_filename": item.original_filename,
                            "file": item.file.url,
                            "inspection": (
                                item.inspection.id
                                if item.inspection
                                else None
                            ),
                            "notes": item.notes,
                        },
                    }
                )

        # Sort newest records first
        records.sort(
            key=lambda record: record["created_at"],
            reverse=True,
        )

        serializer = self.get_serializer(records, many=True)

        return Response(serializer.data)