# Generated by Django 5.0.1 on 2024-02-01 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bunkerusers', '0003_user_showman'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='host',
            field=models.BooleanField(db_default=models.Value(False), default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='ready',
            field=models.BooleanField(db_default=models.Value(False), default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='showman',
            field=models.BooleanField(db_default=models.Value(False), default=False),
        ),
    ]
