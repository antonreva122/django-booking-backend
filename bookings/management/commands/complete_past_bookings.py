from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking


class Command(BaseCommand):
    help = "Mark past PENDING/CONFIRMED bookings as COMPLETED"

    def handle(self, *args, **options):
        today = timezone.now().date()
        updated = Booking.objects.filter(
            booking_date__lt=today,
            status__in=["PENDING", "CONFIRMED"],
        ).update(status="COMPLETED")

        self.stdout.write(
            self.style.SUCCESS(f"Marked {updated} past booking(s) as COMPLETED")
        )
