import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or promote the deployment administrator."

    def handle(self, *args, **options):
        username = os.environ.get("DEPLOYMENT_ADMIN_USERNAME")
        password = os.environ.get("DEPLOYMENT_ADMIN_PASSWORD")

        if not username or not password:
            raise CommandError(
                "Set DEPLOYMENT_ADMIN_USERNAME and "
                "DEPLOYMENT_ADMIN_PASSWORD in the deployment environment."
            )

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"is_staff": True, "is_superuser": True},
        )

        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} deployment administrator: {username}"
            )
        )