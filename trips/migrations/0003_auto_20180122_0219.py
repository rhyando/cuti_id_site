# Generated by Django 2.0 on 2018-01-21 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0002_auto_20180122_0210'),
    ]

    operations = [
        migrations.AddField(
            model_name='subdestination',
            name='pardestination',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='trips.Destination'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subdestination',
            name='subdestination',
            field=models.CharField(max_length=200),
        ),
    ]
