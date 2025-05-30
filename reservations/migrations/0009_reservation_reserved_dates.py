
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0008_reservation_letter'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='reserved_dates',
            field=models.CharField(blank=True, help_text='Comma-separated list of all reserved dates for multi-date reservations', max_length=512, null=True),
        ),
    ]
