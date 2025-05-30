
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_remove_reservation_time_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='admin_approvals',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='reservation',
            name='admin_rejections',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
