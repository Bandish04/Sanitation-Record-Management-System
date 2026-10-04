from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from plants.models import Plant

from .serializers import SanitizerTitrationSerializer


class SanitizerTitrationTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(
            username="test_sanitizer_user",
            password="TestPassword123",
        )

        cls.plant = Plant.objects.create(
            code="TEST_PLANT",
            name="Test Plant",
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


    def test_sanitizer_calculation(self):

        serializer = SanitizerTitrationSerializer(
            data={
                "plant": self.plant.id,
                "r71_drops": 4,
            },
            context=self.get_request_context(),
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        titration = serializer.save()

        self.assertEqual(
            titration.r71_drops,
            4,
        )

        self.assertEqual(
            titration.ppm,
            Decimal("50.0"),
        )

        self.assertEqual(
            titration.percent_vv,
            Decimal("0.0500"),
        )

        self.assertEqual(
            titration.sample_volume_ml,
            Decimal("5.00"),
        )


    def test_sanitizer_minimum_drops_validation(self):

        serializer = SanitizerTitrationSerializer(
            data={
                "plant": self.plant.id,
                "r71_drops": 0,
            },
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "r71_drops",
            serializer.errors,
        )


    def test_sanitizer_maximum_drops_validation(self):

        serializer = SanitizerTitrationSerializer(
            data={
                "plant": self.plant.id,
                "r71_drops": 33,
            },
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "r71_drops",
            serializer.errors,
        )


    def test_sanitizer_valid_maximum_drops(self):

        serializer = SanitizerTitrationSerializer(
            data={
                "plant": self.plant.id,
                "r71_drops": 32,
            },
            context=self.get_request_context(),
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        titration = serializer.save()

        self.assertEqual(
            titration.ppm,
            Decimal("400.0"),
        )

        self.assertEqual(
            titration.percent_vv,
            Decimal("0.4000"),
        )