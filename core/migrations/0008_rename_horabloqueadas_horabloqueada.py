# Generated by Django 5.1.5 on 2025-04-14 21:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_horasbloqueadas_horabloqueadas_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HoraBloqueadas',
            new_name='HoraBloqueada',
        ),
    ]
