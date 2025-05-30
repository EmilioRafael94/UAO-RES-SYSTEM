
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reservations', '0009_reservation_reserved_dates'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ManpowerNeeded',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manpower_type', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userportal_manpower_needed', to='reservations.reservation')),
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
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='other_facilities', to='reservations.reservation')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('role', models.CharField(choices=[('Student of XU', 'Student of XU'), ('Alumni/Guest', 'Alumni/Guest')], default='Student of XU', max_length=20)),
                ('id_type', models.CharField(blank=True, max_length=50, null=True)),
                ('id_upload', models.FileField(blank=True, null=True, upload_to='id_uploads/')),
                ('is_verified', models.BooleanField(default=False)),
                ('verification_code', models.CharField(blank=True, max_length=6, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
