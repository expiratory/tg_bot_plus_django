# Generated by Django 5.0.2 on 2024-02-09 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='post_data',
            field=models.TextField(default=''),
        ),
    ]