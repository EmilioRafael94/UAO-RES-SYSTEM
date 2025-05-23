from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Delete users who are not allowed (not @my.xu.edu.ph and not superuser/staff)'

    def handle(self, *args, **options):
        deleted = 0
        for user in User.objects.all():
            if not user.is_superuser and not user.is_staff and not user.email.endswith('@my.xu.edu.ph'):
                user.delete()
                deleted += 1
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} unauthorized users.'))
