
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_portal', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=255)),
                ('representative', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=20)),
                ('date_reserved', models.DateField()),
                ('insider_count', models.PositiveIntegerField(default=0)),
                ('outsider_count', models.PositiveIntegerField(default=0)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('facility', models.CharField(max_length=255)),
                ('event_type', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Completed', 'Completed')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('notification_type', models.CharField(default='general', max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OtherFacility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facility_name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='other_facilities', to='user_portal.reservation')),
            ],
        ),
        migrations.CreateModel(
            name='ManpowerNeeded',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manpower_type', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manpower_needed', to='user_portal.reservation')),
            ],
        ),
    ]
