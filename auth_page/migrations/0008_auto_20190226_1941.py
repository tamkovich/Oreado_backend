# Generated by Django 2.1 on 2019-02-26 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_page', '0007_auto_20190226_1629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gmailmails',
            old_name='body',
            new_name='text_body',
        ),
        migrations.AddField(
            model_name='gmailmails',
            name='html_body',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
