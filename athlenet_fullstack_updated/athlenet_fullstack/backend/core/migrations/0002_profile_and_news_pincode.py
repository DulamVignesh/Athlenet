import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pincode',
            field=models.CharField(
                blank=True,
                max_length=6,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Enter a valid 6-digit Indian PIN code.',
                        regex='^[1-9][0-9]{5}$',
                    ),
                ],
            ),
        ),
        migrations.AddField(
            model_name='news',
            name='pincode',
            field=models.CharField(
                blank=True,
                max_length=6,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Enter a valid 6-digit Indian PIN code.',
                        regex='^[1-9][0-9]{5}$',
                    ),
                ],
            ),
        ),
    ]
