from datetime import date as date_class
from io import BytesIO
from pathlib import Path

from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

from plants.models import Plant

from titrations.models import (
    SanitizerTitration,
    ChloragelTitration,
)

from inspections.models import (
    SanitationInspection,
    ATPReport,
)


class DailyRecordsPDFAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        plant_id = request.query_params.get("plant")
        date_value = request.query_params.get("date")

        # ==================================================
        # Validate parameters
        # ==================================================

        if not plant_id:
            return Response(
                {
                    "detail": "Plant is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not date_value:
            return Response(
                {
                    "detail": "Date is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            selected_date = date_class.fromisoformat(
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
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # Get Plant
        # ==================================================

        plant = get_object_or_404(
            Plant,
            id=plant_id,
        )

        # ==================================================
        # DAILY RECORDS
        #
        # These filters intentionally match
        # DailyRecordsAPIView.
        # ==================================================

        # -----------------------------------------
        # Sanitizer
        # -----------------------------------------

        sanitizer_records = (
            SanitizerTitration.objects
            .filter(
                plant=plant,
                created_at__date=selected_date,
            )
            .select_related(
                "created_by",
            )
            .order_by("-created_at")
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
            .select_related(
                "created_by",
            )
            .order_by("-created_at")
        )

        # -----------------------------------------
        # Sanitation Inspections
        # -----------------------------------------
        #
        # IMPORTANT:
        # Use inspection_date, NOT created_at__date.
        #

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
                "answers__question",
            )
            .order_by("-created_at")
        )

        # -----------------------------------------
        # ATP Reports
        # -----------------------------------------
        #
        # Match DailyRecordsAPIView:
        # plant + uploaded_at date.
        #

        atp_records = (
            ATPReport.objects
            .filter(
                plant=plant,
                uploaded_at__date=selected_date,
            )
            .select_related(
                "plant",
                "inspection",
                "uploaded_by",
            )
            .order_by("-uploaded_at")
        )

        # ==================================================
        # PDF SETUP
        # ==================================================

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=35,
            leftMargin=35,
            topMargin=35,
            bottomMargin=35,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            leading=22,
            spaceAfter=10,
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            spaceBefore=12,
            spaceAfter=8,
        )

        normal_style = ParagraphStyle(
            "NormalReport",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
        )

        small_style = ParagraphStyle(
            "SmallReport",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
        )

        story = []

        # ==================================================
        # TITLE
        # ==================================================

        story.append(
            Paragraph(
                "DAILY SANITATION REPORT",
                title_style,
            )
        )

        story.append(
            Paragraph(
                (
                    f"<b>Plant:</b> "
                    f"{plant.code} - {plant.name}"
                ),
                normal_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Date:</b> {selected_date.isoformat()}",
                normal_style,
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        # ==================================================
        # REPORT SUMMARY
        # ==================================================

        story.append(
            Paragraph(
                "Report Summary",
                heading_style,
            )
        )

        summary_data = [
            [
                "Record Type",
                "Total Records",
            ],
            [
                "Sanitizer Titrations",
                str(
                    sanitizer_records.count()
                ),
            ],
            [
                "Chloragel Titrations",
                str(
                    chloragel_records.count()
                ),
            ],
            [
                "Sanitation Inspections",
                str(
                    inspection_records.count()
                ),
            ],
            [
                "ATP Reports",
                str(
                    atp_records.count()
                ),
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[
                3.8 * inch,
                1.5 * inch,
            ],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.black,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (0, 1),
                        (-1, -1),
                        "Helvetica",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            summary_table
        )

        # ==================================================
        # SANITIZER TITRATIONS
        # ==================================================

        story.append(
            Paragraph(
                "Sanitizer Titrations",
                heading_style,
            )
        )

        if sanitizer_records.exists():

            sanitizer_data = [
                [
                    "ID",
                    "R-71 Drops",
                    "Sample (ml)",
                    "PPM",
                    "% v/v",
                    "Status",
                    "Created By",
                ]
            ]

            for record in sanitizer_records:

                sanitizer_data.append(
                    [
                        str(record.id),
                        str(record.r71_drops),
                        str(record.sample_volume_ml),
                        str(record.ppm),
                        str(record.percent_vv),
                        str(record.status),
                        str(record.created_by),
                    ]
                )

            sanitizer_table = Table(
                sanitizer_data,
                repeatRows=1,
                colWidths=[
                    0.35 * inch,
                    0.65 * inch,
                    0.75 * inch,
                    0.65 * inch,
                    0.65 * inch,
                    0.85 * inch,
                    1.0 * inch,
                ],
            )

            sanitizer_table.setStyle(
                self._table_style()
            )

            story.append(
                sanitizer_table
            )

        else:

            story.append(
                Paragraph(
                    "No sanitizer titrations found.",
                    normal_style,
                )
            )

        # ==================================================
        # CHLORAGEL TITRATIONS
        # ==================================================

        story.append(
            Paragraph(
                "Chloragel Titrations",
                heading_style,
            )
        )

        if chloragel_records.exists():

            chloragel_data = [
                [
                    "ID",
                    "R-9 Drops",
                    "Sample (ml)",
                    "Result %",
                    "Status",
                    "Created By",
                ]
            ]

            for record in chloragel_records:

                chloragel_data.append(
                    [
                        str(record.id),
                        str(record.r9_drops),
                        str(record.sample_volume_ml),
                        str(record.result_percent),
                        str(record.status),
                        str(record.created_by),
                    ]
                )

            chloragel_table = Table(
                chloragel_data,
                repeatRows=1,
                colWidths=[
                    0.4 * inch,
                    0.7 * inch,
                    0.8 * inch,
                    0.8 * inch,
                    0.9 * inch,
                    1.3 * inch,
                ],
            )

            chloragel_table.setStyle(
                self._table_style()
            )

            story.append(
                chloragel_table
            )

        else:

            story.append(
                Paragraph(
                    "No Chloragel titrations found.",
                    normal_style,
                )
            )

        # ==================================================
        # SANITATION INSPECTIONS
        # ==================================================

        story.append(
            Paragraph(
                "Sanitation Inspections",
                heading_style,
            )
        )

        if inspection_records.exists():

            inspection_data = [
                [
                    "ID",
                    "Inspection Date",
                    "Template",
                    "Status",
                    "Inspector",
                    "Created At",
                ]
            ]

            for record in inspection_records:

                inspection_data.append(
                    [
                        str(record.id),
                        str(record.inspection_date),
                        Paragraph(
                            record.template.name,
                            small_style,
                        ),
                        str(record.status),
                        str(record.inspector.username),
                        Paragraph(
                            str(record.created_at),
                            small_style,
                        ),
                    ]
                )

            inspection_table = Table(
                inspection_data,
                repeatRows=1,
                colWidths=[
                    0.4 * inch,
                    0.85 * inch,
                    1.55 * inch,
                    0.85 * inch,
                    1.0 * inch,
                    1.45 * inch,
                ],
            )

            inspection_table.setStyle(
                self._table_style()
            )

            story.append(
                inspection_table
            )

            # -----------------------------------------
            # Inspection details
            # -----------------------------------------

            for record in inspection_records:

                story.append(
                    Spacer(
                        1,
                        8,
                    )
                )

                story.append(
                    Paragraph(
                        (
                            f"Inspection #{record.id} "
                            f"- Details"
                        ),
                        heading_style,
                    )
                )

                inspection_detail_data = [
                    [
                        "Field",
                        "Value",
                    ],
                    [
                        "Plant",
                        (
                            f"{record.plant.code} - "
                            f"{record.plant.name}"
                        ),
                    ],
                    [
                        "Inspection Date",
                        str(
                            record.inspection_date
                        ),
                    ],
                    [
                        "Template",
                        record.template.name,
                    ],
                    [
                        "Inspector",
                        record.inspector.username,
                    ],
                    [
                        "Status",
                        record.status,
                    ],
                    [
                        "Signed At",
                        (
                            str(record.signed_at)
                            if record.signed_at
                            else ""
                        ),
                    ],
                    [
                        "General Notes",
                        (
                            record.general_notes
                            or ""
                        ),
                    ],
                ]

                inspection_detail_table = Table(
                    inspection_detail_data,
                    colWidths=[
                        1.5 * inch,
                        4.8 * inch,
                    ],
                )

                inspection_detail_table.setStyle(
                    self._table_style()
                )

                story.append(
                    inspection_detail_table
                )

                # -----------------------------------------
                # Answers
                # -----------------------------------------

                answers = record.answers.all()

                if answers:

                    answer_data = [
                        [
                            "Question",
                            "Answer",
                            "Observation",
                        ]
                    ]

                    for answer in answers:

                        answer_data.append(
                            [
                                Paragraph(
                                    answer.question.question_text,
                                    small_style,
                                ),
                                str(
                                    answer.answer
                                ),
                                Paragraph(
                                    answer.observation
                                    or "",
                                    small_style,
                                ),
                            ]
                        )

                    answer_table = Table(
                        answer_data,
                        repeatRows=1,
                        colWidths=[
                            3.0 * inch,
                            0.75 * inch,
                            2.55 * inch,
                        ],
                    )

                    answer_table.setStyle(
                        self._table_style()
                    )

                    story.append(
                        Spacer(
                            1,
                            6,
                        )
                    )

                    story.append(
                        answer_table
                    )

        else:

            story.append(
                Paragraph(
                    "No sanitation inspections found.",
                    normal_style,
                )
            )

        # ==================================================
        # ATP REPORTS
        # ==================================================

        story.append(
            Paragraph(
                "ATP Reports",
                heading_style,
            )
        )

        if atp_records.exists():

            atp_data = [
                [
                    "ID",
                    "Filename",
                    "Inspection",
                    "Uploaded By",
                    "Uploaded At",
                    "Status",
                    "Notes",
                ]
            ]

            for record in atp_records:

                filename = (
                    record.original_filename
                    or ""
                )

                uploaded_at = (
                    str(record.uploaded_at)
                    if record.uploaded_at
                    else ""
                )

                notes = (
                    record.notes
                    or ""
                )

                atp_data.append(
                    [
                        str(record.id),
                        Paragraph(
                            filename,
                            small_style,
                        ),
                        str(
                            record.inspection_id
                            or ""
                        ),
                        str(
                            record.uploaded_by
                        ),
                        Paragraph(
                            uploaded_at,
                            small_style,
                        ),
                        str(
                            record.status
                        ),
                        Paragraph(
                            notes,
                            small_style,
                        ),
                    ]
                )

            atp_table = Table(
                atp_data,
                repeatRows=1,
                colWidths=[
                    0.35 * inch,
                    1.65 * inch,
                    0.65 * inch,
                    0.85 * inch,
                    1.0 * inch,
                    0.65 * inch,
                    1.15 * inch,
                ],
            )

            atp_table.setStyle(
                self._table_style()
            )

            story.append(
                atp_table
            )

            # -----------------------------------------
            # ATP FILE PREVIEW
            # -----------------------------------------

            for record in atp_records:

                if not record.file:
                    continue

                try:

                    file_path = Path(
                        record.file.path
                    )

                except Exception:

                    continue

                if not file_path.exists():
                    continue

                image_extensions = [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".bmp",
                    ".webp",
                ]

                if (
                    file_path.suffix.lower()
                    not in image_extensions
                ):
                    continue

                story.append(
                    Spacer(
                        1,
                        15,
                    )
                )

                story.append(
                    Paragraph(
                        (
                            "ATP File Preview - "
                            f"{record.original_filename}"
                        ),
                        heading_style,
                    )
                )

                try:

                    atp_image = Image(
                        str(file_path),
                        width=5.5 * inch,
                        height=5.5 * inch,
                    )

                    atp_image.hAlign = "CENTER"

                    story.append(
                        atp_image
                    )

                except Exception:

                    story.append(
                        Paragraph(
                            (
                                "Unable to display "
                                "the ATP image."
                            ),
                            normal_style,
                        )
                    )

        else:

            story.append(
                Paragraph(
                    "No ATP reports found.",
                    normal_style,
                )
            )

        # ==================================================
        # BUILD PDF
        # ==================================================

        doc.build(
            story
        )

        buffer.seek(0)

        filename = (
            f"daily_records_"
            f"{plant.code}_"
            f"{selected_date.isoformat()}.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )

    # ==================================================
    # TABLE STYLE
    # ==================================================

    @staticmethod
    def _table_style():

        return TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7.5,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )