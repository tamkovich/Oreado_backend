# Generated by Django 2.1 on 2019-03-24 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0006_auto_20190324_1203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mail',
            name='date_mail',
        ),
    ]