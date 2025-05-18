from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('superuser_portal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockeddate',
            name='start_time',
            field=models.TimeField(default='08:00:00'),
        ),
        migrations.AddField(
            model_name='blockeddate',
            name='end_time',
            field=models.TimeField(default='17:00:00'),
        ),
    ]
