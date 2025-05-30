
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('start_time', models.TimeField(default='00:00:00')),
                ('end_time', models.TimeField(default='00:00:00')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], max_length=20)),
                ('organization', models.CharField(blank=True, max_length=100, null=True)),
                ('representative', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True)),
                ('event_type', models.CharField(blank=True, max_length=50, null=True)),
                ('insider_count', models.IntegerField(default=0)),
                ('outsider_count', models.IntegerField(default=0)),
                ('facilities_needed', models.JSONField(blank=True, null=True)),
                ('manpower_needed', models.JSONField(blank=True, null=True)),
                ('reasons', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_reservations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
