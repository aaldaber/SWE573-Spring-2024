# Generated by Django 4.2 on 2024-05-12 20:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0006_community_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='view_count',
            field=models.BigIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='PostViews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_date', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post View',
                'verbose_name_plural': 'Post Views',
                'unique_together': {('post', 'user')},
            },
        ),
    ]
