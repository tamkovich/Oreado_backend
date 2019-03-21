# Generated by Django 2.1 on 2019-03-14 22:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("auth_page", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Mail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message_id", models.CharField(max_length=100)),
                ("date", models.CharField(max_length=100)),
                ("come_from", models.CharField(max_length=100)),
                ("go_to", models.CharField(max_length=100)),
                ("text_body", models.TextField()),
                ("html_body", models.TextField()),
                ("tag_body", models.TextField()),
                ("snippet", models.TextField()),
                ("blocked", models.BooleanField(default=False)),
                ("viewed", models.BooleanField(default=False)),
                ("favourite", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="MailCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True)),
                ("css_class", models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name="mail",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="mails.MailCategory",
            ),
        ),
        migrations.AddField(
            model_name="mail",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="auth_page.Credential",
            ),
        ),
    ]
