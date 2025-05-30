
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
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='Pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('billing_statement', models.FileField(blank=True, null=True, upload_to='billing_statements/')),
                ('payment_receipt', models.FileField(blank=True, null=True, upload_to='receipts/')),
                ('security_pass', models.FileField(blank=True, null=True, upload_to='passes/')),
                ('facility', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time_slot', models.TimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
