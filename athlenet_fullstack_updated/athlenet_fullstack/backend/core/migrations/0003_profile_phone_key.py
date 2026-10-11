import re
from collections import Counter

from django.db import migrations, models


def populate_phone_keys(apps, schema_editor):
    Profile = apps.get_model('core', 'Profile')
    profiles = list(Profile.objects.exclude(phone='').only('id', 'phone'))

    def normalize(phone):
        digits = re.sub(r'\D', '', phone or '')
        if len(digits) == 12 and digits.startswith('91'):
            digits = digits[2:]
        return digits if len(digits) == 10 else ''

    counts = Counter(normalize(profile.phone) for profile in profiles)
    for profile in profiles:
        key = normalize(profile.phone)
        if key and counts[key] == 1:
            Profile.objects.filter(pk=profile.pk).update(phone_key=key)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_profile_and_news_pincode'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone_key',
            field=models.CharField(blank=True, editable=False, max_length=10, null=True, unique=True),
        ),
        migrations.RunPython(populate_phone_keys, migrations.RunPython.noop),
    ]
