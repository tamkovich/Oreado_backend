# Generated by Django 2.1 on 2019-02-26 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_page', '0003_auto_20190225_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='GmailMails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.CharField(max_length=30)),
                ('date', models.CharField(max_length=30)),
                ('come_from', models.CharField(max_length=30)),
                ('go_to', models.CharField(max_length=30)),
                ('body', models.TextField()),
                ('snippet', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MailCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField()),
            ],
        ),
        migrations.AddField(
            model_name='gmailmails',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth_page.MailCategory'),
        ),
    ]
