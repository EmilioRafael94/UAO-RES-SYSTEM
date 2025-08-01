
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reservation',
            options={'ordering': ['-date', '-created_at'], 'verbose_name': 'Reservation', 'verbose_name_plural': 'Reservations'},
        ),
        migrations.AddField(
            model_name='reservation',
            name='admin_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='contact_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='reservation',
            name='date_reserved',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='end_time',
            field=models.TimeField(default='00:00:00'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='event_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='reservation',
            name='facilities_needed',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='reservation',
            name='facility_use',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='reservation',
            name='insider_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reservation',
            name='manpower_needed',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='reservation',
            name='organization',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='reservation',
            name='outsider_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reservation',
            name='reasons',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='rejection_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='representative',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='reservation',
            name='start_time',
            field=models.TimeField(default='00:00:00'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Cancelled', 'Cancelled')], default='Pending', max_length=50),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to=settings.AUTH_USER_MODEL),
        ),
    ]
