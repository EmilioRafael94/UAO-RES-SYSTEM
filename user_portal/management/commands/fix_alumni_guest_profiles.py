from django.core.management.base import BaseCommand
from user_portal.models import Profile

class Command(BaseCommand):
    help = 'Force all non-student users (not @my.xu.edu.ph) to Alumni/Guest and clear their course.'

    def handle(self, *args, **options):
        updated = 0
        for profile in Profile.objects.all():
            if not profile.user.email.endswith('@my.xu.edu.ph') or profile.user.username == 'guest' or profile.role != 'Student of XU':
                profile.role = 'Alumni/Guest'
                profile.course = ''
                profile.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} alumni/guest profiles.'))
