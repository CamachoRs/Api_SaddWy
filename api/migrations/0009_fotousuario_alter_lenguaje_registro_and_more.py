# Generated by Django 5.0.3 on 2024-03-12 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_usuario_foto'),
    ]

    operations = [
        migrations.CreateModel(
            name='FotoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(upload_to='predeterminados/')),
            ],
        ),
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