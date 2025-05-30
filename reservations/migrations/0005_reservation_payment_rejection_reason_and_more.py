
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_reservation_admin_approvals_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='payment_rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='payment_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reservation',
            name='payment_verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_payments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reservation',
            name='payment_verified_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Admin Approved', 'Admin Approved'), ('Billing Uploaded', 'Billing Uploaded'), ('Payment Pending', 'Payment Pending'), ('Payment Approved', 'Payment Approved'), ('Security Pass Issued', 'Security Pass Issued'), ('Completed', 'Completed'), ('Rejected', 'Rejected'), ('Cancelled', 'Cancelled')], default='Pending', max_length=50),
        ),
    ]
