import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reservations.models import Reservation
from django.utils import timezone

def check_reservations():
    print("\n=== All Reservations ===")
    all_reservations = Reservation.objects.all()
    for res in all_reservations:
        print(f"\nID: {res.id}")
        print(f"User: {res.user.username}")
        print(f"Facility: {res.facility_use}")
        print(f"Date: {res.date}")
        print(f"Status: {res.status}")
        print(f"Created at: {res.created_at}")
        print(f"Updated at: {res.updated_at}")
        print("-" * 50)

    print("\n=== Pending Reservations ===")
    pending = Reservation.objects.filter(status='Pending')
    print(f"Count: {pending.count()}")
    for res in pending:
        print(f"ID: {res.id} - {res.facility_use} on {res.date}")

    print("\n=== Approved Reservations ===")
    approved = Reservation.objects.filter(status='Approved')
    print(f"Count: {approved.count()}")
    for res in approved:
        print(f"ID: {res.id} - {res.facility_use} on {res.date}")

    print("\n=== Rejected Reservations ===")
    rejected = Reservation.objects.filter(status='Rejected')
    print(f"Count: {rejected.count()}")
    for res in rejected:
        print(f"ID: {res.id} - {res.facility_use} on {res.date}")

if __name__ == "__main__":
    check_reservations() 