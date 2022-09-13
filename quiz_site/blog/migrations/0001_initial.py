# Generated by Django 4.1 on 2022-09-12 10:26

import blog.models
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.blocks
import wagtail.contrib.routable_page.models
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0076_modellogentry_revision'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(allow_unicode=True, help_text='A slug to identify posts by this category', max_length=255, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Blog Category',
                'verbose_name_plural': 'Blog Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BlogListingPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('custom_title', models.CharField(help_text='Overwrites the default title', max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtail.contrib.routable_page.models.RoutablePageMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='BlogPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('date', models.DateField(default=blog.models.default_date_time, verbose_name='Post date')),
                ('intro', wagtail.fields.StreamField([('article_section', wagtail.blocks.StructBlock([('content', wagtail.blocks.RichTextBlock(required=False))]))], blank=True, null=True, use_json_field=None)),
                ('title_image', models.ImageField(blank=True, null=True, upload_to='blog_images/title')),
                ('second_intro', wagtail.fields.StreamField([('article_section', wagtail.blocks.StructBlock([('content', wagtail.blocks.RichTextBlock(required=False))]))], blank=True, null=True, use_json_field=None)),
                ('secondary_title', models.CharField(max_length=300)),
                ('secondary_title_image', models.ImageField(blank=True, null=True, upload_to='blog_images/secondary')),
                ('text_before_content', wagtail.fields.StreamField([('article_section', wagtail.blocks.StructBlock([('content', wagtail.blocks.RichTextBlock(required=False))]))], blank=True, null=True, use_json_field=None)),
                ('content', wagtail.fields.StreamField([('article_section', wagtail.blocks.StructBlock([('header', wagtail.blocks.CharBlock(required=False)), ('content', wagtail.blocks.RichTextBlock(required=False))]))], use_json_field=None)),
                ('categories', modelcluster.fields.ParentalManyToManyField(blank=True, to='blog.blogcategory')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
