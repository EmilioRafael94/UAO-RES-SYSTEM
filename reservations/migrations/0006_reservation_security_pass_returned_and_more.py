
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_reservation_payment_rejection_reason_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='security_pass_returned',
            field=models.FileField(blank=True, null=True, upload_to='security_passes/'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='security_pass_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
    ]
