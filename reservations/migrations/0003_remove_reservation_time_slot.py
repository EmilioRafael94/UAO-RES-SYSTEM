
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_alter_reservation_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='time_slot',
        ),
    ]
