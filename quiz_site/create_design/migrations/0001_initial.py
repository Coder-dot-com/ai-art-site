# Generated by Django 4.1 on 2022-09-13 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('quiz_backend', '0002_remove_questionchoice_font_file_and_more'),
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreateDesignRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orientation', models.CharField(choices=[('Landscape', 'Landscape'), ('Portrait', 'Portrait'), ('Square', 'Square')], max_length=500)),
                ('image', models.ImageField(upload_to='user_uploads/')),
                ('effect', models.CharField(choices=[('Landscape', 'Landscape'), ('Portrait', 'Portrait'), ('Square', 'Square')], max_length=500)),
                ('date_of_request', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('requested', 'requested'), ('created', 'created')], max_length=300)),
                ('email', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.useremail')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz_backend.usersession')),
            ],
        ),
    ]
