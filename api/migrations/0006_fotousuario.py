# Generated by Django 5.0.3 on 2024-03-09 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_usuariotoken_idusuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='FotoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(upload_to='predeterminados/')),
            ],
        ),
    ]
