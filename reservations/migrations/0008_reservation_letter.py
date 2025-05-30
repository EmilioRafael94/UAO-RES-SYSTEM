
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0007_reservation_security_pass_rejection_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='letter',
            field=models.FileField(blank=True, null=True, upload_to='letters/'),
        ),
    ]
