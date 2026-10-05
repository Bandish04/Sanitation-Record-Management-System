from datetime import date, datetime, time, timedelta

from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication,
)

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from plants.models import Plant

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


class CombinedRecordsAPIView(generics.ListAPIView):

    serializer_class = CombinedRecordSerializer

    permission_classes = [
        IsAuthenticated
    ]

    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

    def get(self, request, *args, **kwargs):

        plant_id = request.query_params.get(
            "plant"
        )

        date_value = request.query_params.get(
            "date"
        )

        start_date = request.query_params.get(
            "start_date"
        )

        end_date = request.query_params.get(
            "end_date"
        )

        status_value = request.query_params.get(
            "status"
        )

        record_type = request.query_params.get(
            "record_type"
        )

        records = []

        # ==================================================
        # SANITIZER / MAXQUAT
        # ==================================================

        if (
            not record_type
            or record_type == "sanitizer"
        ):

            sanitizer_queryset = (
                SanitizerTitration.objects
                .select_related(
                    "plant",
                    "created_by",
                )
                .order_by(
                    "-created_at"
                )
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

                record = {
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
                        "percent_vv": str(
                            item.percent_vv
                        ),
                        "result_status": item.result_status,
                    },
                }

                records.append(record)

        # ==================================================
        # CHLORAGEL
        # ==================================================

        if (
            not record_type
            or record_type == "chloragel"
        ):

            chloragel_queryset = (
                ChloragelTitration.objects
                .select_related(
                    "plant",
                    "created_by",
                )
                .order_by(
                    "-created_at"
                )
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

                record = {
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
                        "result_status": item.result_status,
                    },
                }

                records.append(record)

        # ==================================================
        # SANITATION INSPECTIONS
        # ==================================================

        if (
            not record_type
            or record_type == "inspection"
        ):

            inspection_queryset = (
                SanitationInspection.objects
                .select_related(
                    "plant",
                    "template",
                    "inspector",
                )
                .prefetch_related(
                    "answers__question"
                )
                .order_by(
                    "-created_at"
                )
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

                record = {
                    "id": item.id,
                    "record_type": "inspection",
                    "plant": item.plant.id,
                    "plant_code": item.plant.code,
                    "plant_name": item.plant.name,
                    "status": item.status,
                    "date": item.inspection_date,
                    "created_by": item.inspector.id,
                    "created_by_username": (
                        item.inspector.username
                    ),
                    "created_at": item.created_at,
                    "data": {
                        "template": item.template.name,
                        "template_name": item.template.name,
                        "template_id": item.template.id,
                        "inspection_date": item.inspection_date,
                        "general_notes": item.general_notes,
                        "signed_at": item.signed_at,
                        "inspector": item.inspector.username,
                        "inspector_name": (
                            item.inspector.username
                        ),
                        "inspector_id": item.inspector.id,
                        "answers": answers,
                    },
                }

                records.append(record)

        # ==================================================
        # ATP REPORTS
        # ==================================================

        if (
            not record_type
            or record_type == "atp"
        ):

            atp_queryset = (
                ATPReport.objects
                .select_related(
                    "plant",
                    "inspection",
                    "uploaded_by",
                    "inspection__inspector",
                )
                .order_by(
                    "-uploaded_at"
                )
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

                inspection_inspector = None

                if item.inspection:
                    inspection_inspector = (
                        item.inspection.inspector.username
                    )

                record = {
                    "id": item.id,
                    "record_type": "atp",
                    "plant": item.plant.id,
                    "plant_code": item.plant.code,
                    "plant_name": item.plant.name,
                    "status": item.status,
                    "date": item.uploaded_at.date(),
                    "created_by": item.uploaded_by.id,
                    "created_by_username": (
                        item.uploaded_by.username
                    ),
                    "created_at": item.uploaded_at,
                    "data": {
                        "original_filename": (
                            item.original_filename
                        ),
                        "file": item.file.url,
                        "inspection": (
                            item.inspection.id
                            if item.inspection
                            else None
                        ),
                        "inspection_inspector": (
                            inspection_inspector
                        ),
                        "notes": item.notes,
                    },
                }

                records.append(record)

        # ==================================================
        # SORT ALL RECORDS
        # ==================================================

        records.sort(
            key=lambda record: record["created_at"],
            reverse=True,
        )

        serializer = self.get_serializer(
            records,
            many=True,
        )

        return Response(
            serializer.data,
            status=200,
        )


class DailyRecordsAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated
    ]

    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

    serializer_class = DailyRecordsSerializer

    def get(self, request):

        plant_id = request.query_params.get(
            "plant"
        )

        date_value = request.query_params.get(
            "date"
        )

        # ==================================================
        # VALIDATE PLANT
        # ==================================================

        if not plant_id:

            return Response(
                {
                    "detail": (
                        "The plant parameter is required."
                    )
                },
                status=400,
            )

        # ==================================================
        # VALIDATE DATE
        # ==================================================

        if not date_value:

            return Response(
                {
                    "detail": (
                        "The date parameter is required."
                    )
                },
                status=400,
            )

        try:

            selected_date = date.fromisoformat(
                date_value
            )

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

        # ==================================================
        # GET PLANT
        # ==================================================

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

        # ==================================================
        # CHECK ADMIN
        # ==================================================

        is_admin = request.user.groups.filter(
            name="Admin"
        ).exists()

        # ==================================================
        # LOCAL DAY BOUNDARIES
        # ==================================================

        local_start = timezone.make_aware(
            datetime.combine(
                selected_date,
                time.min,
            )
        )

        local_end = (
            local_start +
            timedelta(days=1)
        )

        # ==================================================
        # SANITIZER RECORDS
        # ==================================================

        sanitizer_records = (
            SanitizerTitration.objects
            .filter(
                plant=plant,
                created_at__gte=local_start,
                created_at__lt=local_end,
            )
            .select_related(
                "created_by"
            )
            .order_by(
                "-created_at"
            )
        )

        sanitizer_data = []

        for item in sanitizer_records:

            sanitizer_data.append(
                {
                    "id": (
                        item.id
                        if is_admin
                        else None
                    ),
                    "r71_drops": item.r71_drops,
                    "sample_volume_ml": str(
                        item.sample_volume_ml
                    ),
                    "ppm": str(item.ppm),
                    "percent_vv": str(
                        item.percent_vv
                    ),
                    "status": item.status,
                    "result_status": (
                        item.result_status
                    ),
                    "created_by": (
                        item.created_by.username
                    ),
                    "created_by_id": (
                        item.created_by.id
                    ),
                    "created_at": item.created_at,
                }
            )

        # ==================================================
        # CHLORAGEL RECORDS
        # ==================================================

        chloragel_records = (
            ChloragelTitration.objects
            .filter(
                plant=plant,
                created_at__gte=local_start,
                created_at__lt=local_end,
            )
            .select_related(
                "created_by"
            )
            .order_by(
                "-created_at"
            )
        )

        chloragel_data = []

        for item in chloragel_records:

            chloragel_data.append(
                {
                    "id": (
                        item.id
                        if is_admin
                        else None
                    ),
                    "r9_drops": item.r9_drops,
                    "sample_volume_ml": str(
                        item.sample_volume_ml
                    ),
                    "result_percent": str(
                        item.result_percent
                    ),
                    "status": item.status,
                    "result_status": (
                        item.result_status
                    ),
                    "created_by": (
                        item.created_by.username
                    ),
                    "created_by_id": (
                        item.created_by.id
                    ),
                    "created_at": item.created_at,
                }
            )

        # ==================================================
        # SANITATION INSPECTIONS
        # ==================================================

        inspection_records = (
            SanitationInspection.objects
            .filter(
                plant=plant,
                inspection_date=selected_date,
            )
            .select_related(
                "plant",
                "template",
                "inspector",
            )
            .prefetch_related(
                "answers__question"
            )
            .order_by(
                "-created_at"
            )
        )

        inspection_data = []

        for item in inspection_records:

            answers = []

            for answer in item.answers.all():

                answers.append(
                    {
                        "question_id": (
                            answer.question.id
                        ),
                        "question": (
                            answer.question.question_text
                        ),
                        "answer": answer.answer,
                        "observation": (
                            answer.observation
                        ),
                    }
                )

            inspection_data.append(
                {
                    "id": (
                        item.id
                        if is_admin
                        else None
                    ),

                    "plant": item.plant.id,

                    "plant_code": (
                        item.plant.code
                    ),

                    "plant_name": (
                        item.plant.name
                    ),

                    # Human-readable template name
                    "template": (
                        item.template.name
                    ),

                    # Explicit human-readable template name
                    "template_name": (
                        item.template.name
                    ),

                    # Template database ID
                    "template_id": (
                        item.template.id
                    ),

                    "status": item.status,

                    "inspection_date": (
                        item.inspection_date
                    ),

                    # Human-readable inspector username
                    "inspector": (
                        item.inspector.username
                    ),

                    # Explicit human-readable inspector name
                    "inspector_name": (
                        item.inspector.username
                    ),

                    # Inspector database ID
                    "inspector_id": (
                        item.inspector.id
                    ),

                    "general_notes": (
                        item.general_notes
                    ),

                    "signed_at": (
                        item.signed_at
                    ),

                    "answers": answers,

                    "created_at": (
                        item.created_at
                    ),
                }
            )

        # ==================================================
        # ATP REPORTS
        # ==================================================

        atp_records = (
            ATPReport.objects
            .filter(
                plant=plant,
                uploaded_at__gte=local_start,
                uploaded_at__lt=local_end,
            )
            .select_related(
                "plant",
                "inspection",
                "uploaded_by",
                "inspection__inspector",
            )
            .order_by(
                "-uploaded_at"
            )
        )

        atp_data = []

        for item in atp_records:

            inspection_inspector = None

            if item.inspection:

                inspection_inspector = (
                    item.inspection.inspector.username
                )

            atp_data.append(
                {
                    "id": (
                        item.id
                        if is_admin
                        else None
                    ),

                    "plant": item.plant.id,

                    "plant_code": (
                        item.plant.code
                    ),

                    "plant_name": (
                        item.plant.name
                    ),

                    "original_filename": (
                        item.original_filename
                    ),

                    "file": item.file.url,

                    "file_url": item.file.url,

                    "inspection": (
                        item.inspection.id
                        if (
                            item.inspection
                            and is_admin
                        )
                        else None
                    ),

                    "inspection_inspector": (
                        inspection_inspector
                    ),

                    "uploaded_by": (
                        item.uploaded_by.username
                    ),

                    "uploaded_by_id": (
                        item.uploaded_by.id
                    ),

                    "uploaded_at": (
                        item.uploaded_at
                    ),

                    "status": item.status,

                    "notes": item.notes,
                }
            )

        # ==================================================
        # DAILY RESPONSE
        # ==================================================

        daily_data = {
            "plant": plant.id,

            "plant_code": plant.code,

            "plant_name": plant.name,

            "date": selected_date,

            "sanitizer_titrations": (
                sanitizer_data
            ),

            "chloragel_titrations": (
                chloragel_data
            ),

            "inspections": (
                inspection_data
            ),

            "atp_reports": (
                atp_data
            ),
        }

        serializer = self.get_serializer(
            daily_data
        )

        return Response(
            serializer.data,
            status=200,
        )