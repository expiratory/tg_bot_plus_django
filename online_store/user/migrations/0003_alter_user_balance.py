# Generated by Django 5.0.2 on 2024-02-11 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_user_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='balance',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
