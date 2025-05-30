
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_reservation_security_pass_returned_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='security_pass_rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
