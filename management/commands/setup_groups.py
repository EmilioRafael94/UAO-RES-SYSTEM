from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

class Command(BaseCommand):
    help = 'Sets up the Admin group and assigns users to it'

    def handle(self, *args, **options):
        # Create Admin group if it doesn't exist
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Admin group'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin group already exists'))

        # Get all staff users (excluding superusers)
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        
        # Add staff users to Admin group
        for user in staff_users:
            admin_group.user_set.add(user)
            self.stdout.write(self.style.SUCCESS(f'Added {user.username} to Admin group')) 