# Generated by Django 2.0.4 on 2018-04-03 20:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_postimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postattribute',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='posts.Post'),
        ),
    ]