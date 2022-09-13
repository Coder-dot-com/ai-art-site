# Generated by Django 4.1 on 2022-09-12 10:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=300, unique=True)),
                ('promo_consent', models.BooleanField(default=False)),
                ('date_time_added', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SentEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_from_email', models.CharField(max_length=200)),
                ('sent_from_name', models.CharField(blank=True, max_length=200)),
                ('email_to_field', models.CharField(max_length=5000)),
                ('email_subject', models.CharField(max_length=300)),
                ('email_content', models.CharField(max_length=5000)),
                ('recipient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.useremail')),
            ],
        ),
    ]
