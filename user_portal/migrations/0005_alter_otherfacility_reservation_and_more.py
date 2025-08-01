
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0011_remove_reservation_payment_receipts_and_more'),
        ('user_portal', '0004_reservation_notification_otherfacility_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otherfacility',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='other_facilities', to='reservations.reservation'),
        ),
        migrations.AlterField(
            model_name='manpowerneeded',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userportal_manpower_needed', to='reservations.reservation'),
        ),
        migrations.DeleteModel(
            name='Reservation',
        ),
    ]
