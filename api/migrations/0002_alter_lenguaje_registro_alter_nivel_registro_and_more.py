# Generated by Django 5.0.2 on 2024-03-03 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lenguaje',
            name='registro',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='nivel',
            name='registro',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='pregunta',
            name='registro',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='progreso',
            name='registro',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='registro',
            field=models.DateField(auto_now_add=True),
        ),
    ]
