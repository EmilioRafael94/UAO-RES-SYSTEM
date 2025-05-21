from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_portal.models import Profile

class Command(BaseCommand):
    help = 'Mark all Google users with @my.xu.edu.ph emails as verified.'

    def handle(self, *args, **options):
        updated = 0
        for profile in Profile.objects.filter(is_verified=False):
            if profile.user.email and profile.user.email.endswith('@my.xu.edu.ph'):
                profile.is_verified = True
                profile.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully marked {updated} Google users as verified.'))
