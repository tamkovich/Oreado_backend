# Generated by Django 2.1 on 2019-03-04 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_page', '0011_gmailmails_blocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gmailmails',
            name='come_from',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='gmailmails',
            name='date',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='gmailmails',
            name='go_to',
            field=models.CharField(max_length=100),
        ),
    ]