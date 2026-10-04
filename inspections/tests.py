from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase

from rest_framework.test import APITestCase

from plants.models import Plant

from .models import (
    InspectionTemplate,
    InspectionSection,
    InspectionQuestion,
    SanitationInspection,
    InspectionAnswer,
)

from .serializers import (
    SanitationInspectionSerializer,
    InspectionAnswerSerializer,
)


# ============================================================
# INSPECTION SERIALIZER TESTS
# ============================================================

class SanitationInspectionTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(
            username="test_inspector",
            password="TestPassword123",
        )

        cls.plant = Plant.objects.create(
            code="TEST_INSPECTION",
            name="Test Inspection Plant",
            active=True,
        )

        cls.template = InspectionTemplate.objects.create(
            name="Test Inspection Template",
            description="Template for automated tests",
            active=True,
        )

        cls.section = InspectionSection.objects.create(
            template=cls.template,
            name="General",
            order=1,
        )

        cls.question = InspectionQuestion.objects.create(
            section=cls.section,
            question_text="Is the area clean?",
            order=1,
            requires_observation_on_no=True,
            active=True,
        )

    def get_request_context(self):

        request = type(
            "Request",
            (),
            {
                "user": self.user,
            },
        )()

        return {
            "request": request,
        }

    def test_inspection_creation(self):

        serializer = SanitationInspectionSerializer(
            data={
                "plant": self.plant.id,
                "template": self.template.id,
                "inspection_date": date.today(),
                "general_notes": "Test inspection",
            },
            context=self.get_request_context(),
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        inspection = serializer.save()

        self.assertEqual(
            inspection.inspector,
            self.user,
        )

        self.assertEqual(
            inspection.status,
            SanitationInspection.Status.DRAFT,
        )

        self.assertEqual(
            inspection.plant,
            self.plant,
        )

        self.assertEqual(
            inspection.template,
            self.template,
        )

    def test_no_answer_requires_observation(self):

        inspection = SanitationInspection.objects.create(
            plant=self.plant,
            template=self.template,
            inspection_date=date.today(),
            inspector=self.user,
            status=SanitationInspection.Status.DRAFT,
        )

        request = type(
            "Request",
            (),
            {
                "data": {
                    "inspection": inspection.id,
                }
            },
        )()

        serializer = InspectionAnswerSerializer(
            data={
                "question": self.question.id,
                "answer": InspectionAnswer.AnswerChoices.NO,
                "observation": "",
            },
            context={
                "request": request,
            },
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "observation",
            serializer.errors,
        )

    def test_no_answer_with_observation_is_valid(self):

        inspection = SanitationInspection.objects.create(
            plant=self.plant,
            template=self.template,
            inspection_date=date.today(),
            inspector=self.user,
            status=SanitationInspection.Status.DRAFT,
        )

        request = type(
            "Request",
            (),
            {
                "data": {
                    "inspection": inspection.id,
                }
            },
        )()

        serializer = InspectionAnswerSerializer(
            data={
                "question": self.question.id,
                "answer": InspectionAnswer.AnswerChoices.NO,
                "observation": "Heavy buildup found.",
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_question_from_wrong_template_is_rejected(self):

        second_template = InspectionTemplate.objects.create(
            name="Second Test Template",
            active=True,
        )

        second_section = InspectionSection.objects.create(
            template=second_template,
            name="Second Section",
            order=1,
        )

        wrong_question = InspectionQuestion.objects.create(
            section=second_section,
            question_text="Question from another template?",
            order=1,
            requires_observation_on_no=False,
            active=True,
        )

        inspection = SanitationInspection.objects.create(
            plant=self.plant,
            template=self.template,
            inspection_date=date.today(),
            inspector=self.user,
            status=SanitationInspection.Status.DRAFT,
        )

        request = type(
            "Request",
            (),
            {
                "data": {
                    "inspection": inspection.id,
                }
            },
        )()

        serializer = InspectionAnswerSerializer(
            data={
                "question": wrong_question.id,
                "answer": InspectionAnswer.AnswerChoices.YES,
                "observation": "",
            },
            context={
                "request": request,
            },
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "question",
            serializer.errors,
        )

    def test_duplicate_answer_is_rejected(self):

        inspection = SanitationInspection.objects.create(
            plant=self.plant,
            template=self.template,
            inspection_date=date.today(),
            inspector=self.user,
            status=SanitationInspection.Status.DRAFT,
        )

        InspectionAnswer.objects.create(
            inspection=inspection,
            question=self.question,
            answer=InspectionAnswer.AnswerChoices.YES,
            observation="Everything looks good.",
        )

        request = type(
            "Request",
            (),
            {
                "data": {
                    "inspection": inspection.id,
                }
            },
        )()

        serializer = InspectionAnswerSerializer(
            data={
                "question": self.question.id,
                "answer": InspectionAnswer.AnswerChoices.YES,
                "observation": "Another answer.",
            },
            context={
                "request": request,
            },
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "question",
            serializer.errors,
        )


# ============================================================
# INSPECTION API VIEW TESTS
# ============================================================

class SanitationInspectionAPITest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.inspector = User.objects.create_user(
            username="api_inspector",
            password="TestPassword123",
        )

        # Create the Inspector group.
        inspector_group = Group.objects.create(
            name="Inspector",
        )

        # Assign the test user to the Inspector group.
        cls.inspector.groups.add(
            inspector_group
        )

        cls.other_inspector = User.objects.create_user(
            username="other_inspector",
            password="TestPassword123",
        )

        cls.plant = Plant.objects.create(
            code="API_TEST",
            name="API Test Plant",
            active=True,
        )

        cls.template = InspectionTemplate.objects.create(
            name="API Test Template",
            description="Template for API tests",
            active=True,
        )

        cls.section = InspectionSection.objects.create(
            template=cls.template,
            name="General",
            order=1,
        )

        cls.question = InspectionQuestion.objects.create(
            section=cls.section,
            question_text="Is the area clean?",
            order=1,
            requires_observation_on_no=True,
            active=True,
        )

    def test_inspector_can_create_inspection(self):

        self.client.force_authenticate(
            user=self.inspector
        )

        response = self.client.post(
            "/api/inspections/",
            {
                "plant": self.plant.id,
                "template": self.template.id,
                "inspection_date": date.today(),
                "general_notes": "API test inspection",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["status"],
            "DRAFT",
        )

        self.assertEqual(
            response.data["inspector"],
            self.inspector.id,
        )

    def test_inspector_cannot_edit_another_inspectors_inspection(self):

        inspection = SanitationInspection.objects.create(
            plant=self.plant,
            template=self.template,
            inspection_date=date.today(),
            inspector=self.other_inspector,
            status=SanitationInspection.Status.DRAFT,
            general_notes="Original notes",
        )

        self.client.force_authenticate(
            user=self.inspector
        )

        response = self.client.patch(
            f"/api/inspections/{inspection.id}/",
            {
                "general_notes": "Unauthorized update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        inspection.refresh_from_db()

        self.assertEqual(
            inspection.general_notes,
            "Original notes",
        )