# Generated by Django 2.1 on 2019-03-19 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth_page", "0002_auto_20190318_1503"),
    ]

    operations = [
        migrations.RemoveField(model_name="credential", name="access_token"),
        migrations.RemoveField(model_name="credential", name="refresh_token"),
        migrations.AddField(
            model_name="credential",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
