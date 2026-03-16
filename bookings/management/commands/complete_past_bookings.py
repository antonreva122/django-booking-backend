from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking


class Command(BaseCommand):
    help = "Mark past PENDING/CONFIRMED bookings as COMPLETED"

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        current_time = now.time()

        # Complete bookings from past dates
        past_count = Booking.objects.filter(
            booking_date__lt=today,
            status__in=["PENDING", "CONFIRMED"],
        ).update(status="COMPLETED")

        # Complete today's bookings where end time has passed
        today_count = Booking.objects.filter(
            booking_date=today,
            end_time__lte=current_time,
            status__in=["PENDING", "CONFIRMED"],
        ).update(status="COMPLETED")

        updated = past_count + today_count
        self.stdout.write(
            self.style.SUCCESS(f"Marked {updated} past booking(s) as COMPLETED")
        )
