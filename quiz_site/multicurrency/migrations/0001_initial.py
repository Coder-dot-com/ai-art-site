# Generated by Django 4.1.1 on 2022-09-23 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_display_name', models.CharField(max_length=100, unique=True)),
                ('currency_code', models.CharField(choices=[('USD', 'USD'), ('AUD', 'AUD'), ('GBP', 'GBP'), ('CAD', 'CAD'), ('NZD', 'NZD'), ('EUR', 'EUR')], max_length=100, unique=True)),
                ('currency_symbol', models.CharField(max_length=2)),
                ('one_usd_to_currency_rate', models.FloatField(blank=True, null=True)),
                ('last_updated_rate', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]
