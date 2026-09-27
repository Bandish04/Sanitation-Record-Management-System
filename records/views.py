from datetime import datetime, time

from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from inspections.models import (
    ATPReport,
    SanitationInspection,
)
from titrations.models import (
    SanitizerTitration,
    ChloragelTitration,
)
from .serializers import (
    CombinedRecordSerializer,
    DailyRecordsSerializer,
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

class DailyRecordsAPIView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = DailyRecordsSerializer

    def get(self, request):

        plant_id = request.query_params.get("plant")
        date_value = request.query_params.get("date")

        if not plant_id:
            return Response(
                {
                    "detail": "The plant parameter is required."
                },
                status=400,
            )

        if not date_value:
            return Response(
                {
                    "detail": "The date parameter is required."
                },
                status=400,
            )

        try:
            from datetime import date

            selected_date = date.fromisoformat(date_value)

        except ValueError:

            return Response(
                {
                    "detail": (
                        "Invalid date format. "
                        "Use YYYY-MM-DD."
                    )
                },
                status=400,
            )

        # -----------------------------------------
        # Get Plant
        # -----------------------------------------

        from plants.models import Plant

        try:

            plant = Plant.objects.get(
                id=plant_id
            )

        except Plant.DoesNotExist:

            return Response(
                {
                    "detail": "Plant not found."
                },
                status=404,
            )

        # -----------------------------------------
        # Sanitizer
        # -----------------------------------------

        sanitizer_records = (
            SanitizerTitration.objects
            .filter(
                plant=plant,
                created_at__date=selected_date,
            )
            .select_related("created_by")
        )

        sanitizer_data = []

        for item in sanitizer_records:

            sanitizer_data.append(
                {
                    "id": item.id,
                    "r71_drops": item.r71_drops,
                    "sample_volume_ml": str(
                        item.sample_volume_ml
                    ),
                    "ppm": str(item.ppm),
                    "percent_vv": str(
                        item.percent_vv
                    ),
                    "status": item.status,
                    "created_by": item.created_by.username,
                    "created_at": item.created_at,
                }
            )

        # -----------------------------------------
        # Chloragel
        # -----------------------------------------

        chloragel_records = (
            ChloragelTitration.objects
            .filter(
                plant=plant,
                created_at__date=selected_date,
            )
            .select_related("created_by")
        )

        chloragel_data = []

        for item in chloragel_records:

            chloragel_data.append(
                {
                    "id": item.id,
                    "r9_drops": item.r9_drops,
                    "sample_volume_ml": str(
                        item.sample_volume_ml
                    ),
                    "result_percent": str(
                        item.result_percent
                    ),
                    "status": item.status,
                    "created_by": item.created_by.username,
                    "created_at": item.created_at,
                }
            )

        # -----------------------------------------
        # Inspections
        # -----------------------------------------

        inspection_records = (
            SanitationInspection.objects
            .filter(
                plant=plant,
                inspection_date=selected_date,
            )
            .select_related(
                "template",
                "inspector",
            )
            .prefetch_related(
                "answers__question"
            )
        )

        inspection_data = []

        for item in inspection_records:

            answers = []

            for answer in item.answers.all():

                answers.append(
                    {
                        "question_id": answer.question.id,
                        "question": (
                            answer.question.question_text
                        ),
                        "answer": answer.answer,
                        "observation": answer.observation,
                    }
                )

            inspection_data.append(
                {
                    "id": item.id,
                    "template": item.template.name,
                    "status": item.status,
                    "inspector": item.inspector.username,
                    "general_notes": item.general_notes,
                    "signed_at": item.signed_at,
                    "answers": answers,
                    "created_at": item.created_at,
                }
            )

        # -----------------------------------------
        # ATP Reports
        # -----------------------------------------

        atp_records = (
            ATPReport.objects
            .filter(
                plant=plant,
                uploaded_at__date=selected_date,
            )
            .select_related(
                "inspection",
                "uploaded_by",
            )
        )

        atp_data = []

        for item in atp_records:

            atp_data.append(
                {
                    "id": item.id,
                    "original_filename": (
                        item.original_filename
                    ),
                    "file": item.file.url,
                    "inspection": (
                        item.inspection.id
                        if item.inspection
                        else None
                    ),
                    "uploaded_by": (
                        item.uploaded_by.username
                    ),
                    "uploaded_at": item.uploaded_at,
                    "status": item.status,
                    "notes": item.notes,
                }
            )

        # -----------------------------------------
        # Final Response
        # -----------------------------------------

        daily_data = {
            "plant": plant.id,
            "plant_code": plant.code,
            "plant_name": plant.name,
            "date": selected_date,
            "sanitizer_titrations": sanitizer_data,
            "chloragel_titrations": chloragel_data,
            "inspections": inspection_data,
            "atp_reports": atp_data,
        }

        serializer = self.get_serializer(
            daily_data
        )

        return Response(
            serializer.data,
            status=200,
        )