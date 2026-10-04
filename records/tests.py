from datetime import date, datetime
from io import BytesIO

from pypdf import PdfReader 

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from plants.models import Plant

from titrations.models import (
    SanitizerTitration,
    ChloragelTitration,
)

from inspections.models import (
    ATPReport,
    InspectionTemplate,
    InspectionSection,
    InspectionQuestion,
    SanitationInspection,
    InspectionAnswer,
)


class RecordsAPITestCase(TestCase):

    def setUp(self):

        self.client = APIClient()

        # -----------------------------------------
        # User
        # -----------------------------------------

        self.user = User.objects.create_user(
            username="records_test_user",
            password="testpass123",
        )

        self.client.force_authenticate(
            user=self.user
        )

        # -----------------------------------------
        # Plants
        # -----------------------------------------

        self.plant_a = Plant.objects.create(
            name="Plant A",
            code="PLANT_A",
        )

        self.plant_b = Plant.objects.create(
            name="Plant B",
            code="PLANT_B",
        )

        # -----------------------------------------
        # Inspection Template
        # -----------------------------------------

        self.template = InspectionTemplate.objects.create(
            name="Daily Sanitation Inspection",
            description="Test inspection template",
            active=True,
        )

        self.section = InspectionSection.objects.create(
            template=self.template,
            name="General",
            order=1,
        )

        self.question = InspectionQuestion.objects.create(
            section=self.section,
            question_text="Is the area clean?",
            order=1,
            requires_observation_on_no=True,
            active=True,
        )

    # ==================================================
    # DAILY RECORDS
    # ==================================================

    def test_daily_records_requires_plant(self):

        response = self.client.get(
            "/api/records/daily/",
            {
                "date": "2026-09-28",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["detail"],
            "The plant parameter is required.",
        )

    def test_daily_records_requires_date(self):

        response = self.client.get(
            "/api/records/daily/",
            {
                "plant": self.plant_a.id,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["detail"],
            "The date parameter is required.",
        )

    def test_daily_records_rejects_invalid_date(self):

        response = self.client.get(
            "/api/records/daily/",
            {
                "plant": self.plant_a.id,
                "date": "28-09-2026",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_daily_records_returns_all_record_types(self):

        target_date = date(2026, 9, 28)

        # -----------------------------------------
        # Sanitizer
        # -----------------------------------------

        sanitizer = SanitizerTitration.objects.create(
            plant=self.plant_a,
            r71_drops=4,
            ppm=50.00,
            percent_vv=0.0500,
            status=SanitizerTitration.Status.DRAFT,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        sanitizer.created_at = sanitizer.created_at.replace(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
        )

        sanitizer.save(
            update_fields=[
                "created_at",
            ]
        )

        # -----------------------------------------
        # Chloragel
        # -----------------------------------------

        chloragel = ChloragelTitration.objects.create(
            plant=self.plant_a,
            r9_drops=5,
            result_percent=0.990,
            status=ChloragelTitration.Status.DRAFT,
            result_status=(
                ChloragelTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        chloragel.created_at = chloragel.created_at.replace(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
        )

        chloragel.save(
            update_fields=[
                "created_at",
            ]
        )

        # -----------------------------------------
        # Inspection
        # -----------------------------------------

        inspection = SanitationInspection.objects.create(
            plant=self.plant_a,
            template=self.template,
            inspection_date=target_date,
            inspector=self.user,
            status=SanitationInspection.Status.DRAFT,
            general_notes="Test daily inspection",
        )

        InspectionAnswer.objects.create(
            inspection=inspection,
            question=self.question,
            answer=InspectionAnswer.AnswerChoices.YES,
            observation="Area is clean.",
        )

        # -----------------------------------------
        # ATP
        # -----------------------------------------

        uploaded_file = SimpleUploadedFile(
            "test_atp.pdf",
            b"test pdf content",
            content_type="application/pdf",
        )

        atp_report = ATPReport.objects.create(
            plant=self.plant_a,
            inspection=inspection,
            file=uploaded_file,
            original_filename="test_atp.pdf",
            uploaded_by=self.user,
            status=ATPReport.Status.ACTIVE,
            notes="Test ATP report",
        )
        atp_report.uploaded_at = atp_report.uploaded_at.replace(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
        )
        atp_report.save(
            update_fields=[
            "uploaded_at",
            ]
        )

        # -----------------------------------------
        # Request
        # -----------------------------------------

        response = self.client.get(
            "/api/records/daily/",
            {
                "plant": self.plant_a.id,
                "date": target_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.data

        self.assertEqual(
            data["plant"],
            self.plant_a.id,
        )

        self.assertEqual(
            data["plant_code"],
            "PLANT_A",
        )

        self.assertEqual(
            data["plant_name"],
            "Plant A",
        )

        self.assertEqual(
            data["date"],
            target_date.isoformat(),
        )

        self.assertEqual(
            len(data["sanitizer_titrations"]),
            1,
        )

        self.assertEqual(
            data["sanitizer_titrations"][0]["id"],
            sanitizer.id,
        )

        self.assertEqual(
            data["sanitizer_titrations"][0]["created_by"],
            self.user.username,
        )

        self.assertEqual(
            len(data["chloragel_titrations"]),
            1,
        )

        self.assertEqual(
            data["chloragel_titrations"][0]["id"],
            chloragel.id,
        )

        self.assertEqual(
            len(data["inspections"]),
            1,
        )

        self.assertEqual(
            data["inspections"][0]["id"],
            inspection.id,
        )

        self.assertEqual(
            data["inspections"][0]["template"],
            self.template.name,
        )

        self.assertEqual(
            len(data["inspections"][0]["answers"]),
            1,
        )

        self.assertEqual(
            data["inspections"][0]["answers"][0]["answer"],
            "YES",
        )

        self.assertEqual(
            len(data["atp_reports"]),
            1,
        )

        self.assertEqual(
            data["atp_reports"][0]["original_filename"],
            "test_atp.pdf",
        )

        self.assertEqual(
            data["atp_reports"][0]["uploaded_by"],
            self.user.username,
        )

    def test_daily_records_only_returns_selected_plant(self):

        target_date = date(2026, 9, 28)

        SanitizerTitration.objects.create(
            plant=self.plant_a,
            r71_drops=4,
            ppm=50.00,
            percent_vv=0.0500,
            status=SanitizerTitration.Status.DRAFT,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        SanitizerTitration.objects.create(
            plant=self.plant_b,
            r71_drops=5,
            ppm=62.50,
            percent_vv=0.0625,
            status=SanitizerTitration.Status.DRAFT,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        # Make both records fall on the requested date.
        for item in SanitizerTitration.objects.all():
            item.created_at = item.created_at.replace(
                year=target_date.year,
                month=target_date.month,
                day=target_date.day,
            )
            item.save(
                update_fields=[
                    "created_at",
                ]
            )

        response = self.client.get(
            "/api/records/daily/",
            {
                "plant": self.plant_a.id,
                "date": target_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["sanitizer_titrations"]),
            1,
        )

        self.assertEqual(
            response.data["sanitizer_titrations"][0]["r71_drops"],
            4,
        )

    def test_daily_records_returns_empty_sections_when_no_records_exist(
        self,
    ):

        response = self.client.get(
            "/api/records/daily/",
            {
                "plant": self.plant_a.id,
                "date": "2026-09-28",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["sanitizer_titrations"],
            [],
        )

        self.assertEqual(
            response.data["chloragel_titrations"],
            [],
        )

        self.assertEqual(
            response.data["inspections"],
            [],
        )

        self.assertEqual(
            response.data["atp_reports"],
            [],
        )

    # ==================================================
    # COMBINED RECORDS
    # ==================================================

    def test_combined_records_returns_records(self):

        sanitizer = SanitizerTitration.objects.create(
            plant=self.plant_a,
            r71_drops=4,
            ppm=50.00,
            percent_vv=0.0500,
            status=SanitizerTitration.Status.DRAFT,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        response = self.client.get(
            "/api/records/",
            {
                "plant": self.plant_a.id,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            sanitizer.id,
        )

        self.assertEqual(
            response.data[0]["record_type"],
            "sanitizer",
        )

        self.assertEqual(
            response.data[0]["plant_code"],
            "PLANT_A",
        )

    def test_combined_records_can_filter_by_record_type(self):

        SanitizerTitration.objects.create(
            plant=self.plant_a,
            r71_drops=4,
            ppm=50.00,
            percent_vv=0.0500,
            status=SanitizerTitration.Status.DRAFT,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        ChloragelTitration.objects.create(
            plant=self.plant_a,
            r9_drops=5,
            result_percent=0.990,
            status=ChloragelTitration.Status.DRAFT,
            result_status=(
                ChloragelTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        response = self.client.get(
            "/api/records/",
            {
                "plant": self.plant_a.id,
                "record_type": "sanitizer",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["record_type"],
            "sanitizer",
        )

    def test_combined_records_can_filter_by_status(self):

        SanitizerTitration.objects.create(
            plant=self.plant_a,
            r71_drops=4,
            ppm=50.00,
            percent_vv=0.0500,
            status=SanitizerTitration.Status.DRAFT,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        SanitizerTitration.objects.create(
            plant=self.plant_a,
            r71_drops=10,
            ppm=125.00,
            percent_vv=0.1250,
            status=SanitizerTitration.Status.SUBMITTED,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.user,
        )

        response = self.client.get(
            "/api/records/",
            {
                "plant": self.plant_a.id,
                "status": "SUBMITTED",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["status"],
            "SUBMITTED",
        )

        # ==================================================
    # DAILY PDF
    # ==================================================

    def test_daily_pdf_returns_pdf_response(self):

        target_date = date(2026, 9, 28)

        inspection = SanitationInspection.objects.create(
            plant=self.plant_a,
            template=self.template,
            inspection_date=target_date,
            inspector=self.user,
            status=SanitationInspection.Status.SUBMITTED,
            general_notes="PDF test inspection",
        )

        response = self.client.get(
            "/api/records/daily/pdf/",
            {
                "plant": self.plant_a.id,
                "date": target_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf",
        )

        self.assertIn(
            "daily_records_PLANT_A_2026-09-28.pdf",
            response["Content-Disposition"],
        )

    def test_daily_pdf_uses_inspection_date(self):

        target_date = date(2026, 9, 27)

        inspection = SanitationInspection.objects.create(
            plant=self.plant_a,
            template=self.template,
            inspection_date=target_date,
            inspector=self.user,
            status=SanitationInspection.Status.SUBMITTED,
            general_notes="Inspection date filtering test",
        )

        response = self.client.get(
            "/api/records/daily/pdf/",
            {
                "plant": self.plant_a.id,
                "date": target_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf",
        )

        pdf_content = b"".join(
            response.streaming_content
        )

        reader = PdfReader(
            BytesIO(pdf_content)
        )

        extracted_text = ""

        for page in reader.pages:
            extracted_text += (
                page.extract_text() or ""
            )

        self.assertIn(
            "Sanitation Inspections",
            extracted_text,
        )

        self.assertIn(
            str(inspection.id),
            extracted_text,
        )
       
    def test_daily_pdf_requires_plant(self):

        response = self.client.get(
            "/api/records/daily/pdf/",
            {
                "date": "2026-09-28",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["detail"],
            "Plant is required.",
        )

    def test_daily_pdf_requires_date(self):

        response = self.client.get(
            "/api/records/daily/pdf/",
            {
                "plant": self.plant_a.id,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["detail"],
            "Date is required.",
        )

    def test_daily_pdf_rejects_invalid_date(self):

        response = self.client.get(
            "/api/records/daily/pdf/",
            {
                "plant": self.plant_a.id,
                "date": "28-09-2026",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["detail"],
            "Invalid date format. Use YYYY-MM-DD.",
        )