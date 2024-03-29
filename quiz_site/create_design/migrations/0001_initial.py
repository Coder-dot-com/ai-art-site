# Generated by Django 4.1.1 on 2022-09-24 15:23

import create_design.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('emails', '0001_initial'),
        ('quiz_backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyOptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_of_purchase', models.CharField(choices=[('Canvas', 'Canvas'), ('Print', 'Print'), ('Digital', 'Digital')], max_length=300)),
                ('orientation', models.CharField(blank=True, choices=[('Landscape', 'Landscape'), ('Portrait', 'Portrait'), ('Square', 'Square')], max_length=500, null=True)),
                ('size', models.CharField(blank=True, max_length=500, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ('price_before_sale', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Effect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effect_name', models.CharField(max_length=500, unique=True)),
                ('prompt', models.CharField(max_length=500)),
                ('prompt_strength', models.FloatField()),
                ('active', models.BooleanField(default=True)),
                ('before_image', models.ImageField(blank=True, null=True, upload_to='effects/before/')),
                ('after_image', models.ImageField(blank=True, null=True, upload_to='effects/after/')),
            ],
        ),
        migrations.CreateModel(
            name='CreateDesignRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orientation', models.CharField(choices=[('Landscape', 'Landscape'), ('Portrait', 'Portrait'), ('Square', 'Square')], max_length=500)),
                ('image', models.ImageField(upload_to='user_uploads/')),
                ('date_of_request', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('requested', 'requested'), ('created', 'created')], max_length=300)),
                ('created_design', models.ImageField(blank=True, null=True, upload_to='created_designs/')),
                ('design_preview', models.ImageField(blank=True, null=True, upload_to='design_previews/')),
                ('unique_id', models.CharField(default=create_design.models.random_id, max_length=300)),
                ('effect', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='create_design.effect')),
                ('email', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.useremail')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz_backend.usersession')),
            ],
        ),
    ]
