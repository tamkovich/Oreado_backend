# Generated by Django 2.1 on 2019-03-23 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0003_mailsender_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailsender',
            name='is_active',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]
