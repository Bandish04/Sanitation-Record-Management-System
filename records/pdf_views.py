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
        date = request.query_params.get("date")

        if not plant_id:
            return Response(
                {"detail": "Plant is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not date:
            return Response(
                {"detail": "Date is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        plant = get_object_or_404(
            Plant,
            id=plant_id,
        )

        # -----------------------------------------
        # GET DAILY RECORDS
        # -----------------------------------------

        sanitizer_records = (
            SanitizerTitration.objects.filter(
                plant=plant,
                created_at__date=date,
            ).order_by("id")
        )

        chloragel_records = (
            ChloragelTitration.objects.filter(
                plant=plant,
                created_at__date=date,
            ).order_by("id")
        )

        inspection_records = (
            SanitationInspection.objects.filter(
                plant=plant,
                created_at__date=date,
            ).order_by("id")
        )

        atp_records = (
            ATPReport.objects.filter(
                inspection__plant=plant,
                uploaded_at__date=date,
            ).order_by("id")
        )

        # -----------------------------------------
        # PDF SETUP
        # -----------------------------------------

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

        # -----------------------------------------
        # TITLE
        # -----------------------------------------

        story.append(
            Paragraph(
                "DAILY SANITATION REPORT",
                title_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Plant:</b> {plant.code} - {plant.name}",
                normal_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Date:</b> {date}",
                normal_style,
            )
        )

        story.append(
            Spacer(
                1,
                15,
            )
        )

        # -----------------------------------------
        # REPORT SUMMARY
        # -----------------------------------------

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
                str(sanitizer_records.count()),
            ],
            [
                "Chloragel Titrations",
                str(chloragel_records.count()),
            ],
            [
                "Sanitation Inspections",
                str(inspection_records.count()),
            ],
            [
                "ATP Reports",
                str(atp_records.count()),
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

        story.append(summary_table)

        # -----------------------------------------
        # SANITIZER TITRATIONS
        # -----------------------------------------

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

            story.append(sanitizer_table)

        else:

            story.append(
                Paragraph(
                    "No sanitizer titrations found.",
                    normal_style,
                )
            )

        # -----------------------------------------
        # CHLORAGEL TITRATIONS
        # -----------------------------------------

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

            story.append(chloragel_table)

        else:

            story.append(
                Paragraph(
                    "No Chloragel titrations found.",
                    normal_style,
                )
            )

        # -----------------------------------------
        # SANITATION INSPECTIONS
        # -----------------------------------------

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
                    "Status",
                    "Created By",
                    "Created At",
                ]
            ]

            for record in inspection_records:

                inspection_data.append(
                    [
                        str(record.id),
                        str(record.status),
                        str(record.inspector.username),
                        str(record.created_at),
                    ]
                )

            inspection_table = Table(
                inspection_data,
                repeatRows=1,
                colWidths=[
                    0.5 * inch,
                    1.0 * inch,
                    1.3 * inch,
                    2.5 * inch,
                ],
            )

            inspection_table.setStyle(
                self._table_style()
            )

            story.append(inspection_table)

        else:

            story.append(
                Paragraph(
                    "No sanitation inspections found.",
                    normal_style,
                )
            )

        # -----------------------------------------
        # ATP REPORTS
        # -----------------------------------------

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
                        str(record.uploaded_by),
                        Paragraph(
                            uploaded_at,
                            small_style,
                        ),
                        str(record.status),
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

            story.append(atp_table)

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
                            "Unable to display the ATP image.",
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

        # -----------------------------------------
        # BUILD PDF
        # -----------------------------------------

        doc.build(story)

        buffer.seek(0)

        filename = (
            f"daily_records_{plant.code}_{date}.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )

    # -----------------------------------------
    # TABLE STYLE
    # -----------------------------------------

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