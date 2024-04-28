# Generated by Django 4.2 on 2024-04-28 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_remove_templatefield_field_templatefield_data_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='postfield',
            name='content_textarea',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='postfield',
            name='content_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='templatefield',
            name='data_type',
            field=models.CharField(choices=[('text', 'Text'), ('textarea', 'Text Area'), ('integer', 'Integer'), ('boolean', 'True / False'), ('float', 'Float'), ('date', 'Date'), ('datetime', 'Datetime'), ('file', 'File'), ('image', 'Image')], default='text', max_length=100),
        ),
    ]
