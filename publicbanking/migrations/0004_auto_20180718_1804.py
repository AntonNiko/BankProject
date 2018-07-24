# Generated by Django 2.0.7 on 2018-07-19 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publicbanking', '0003_auto_20180718_0140'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='account_card',
            field=models.IntegerField(blank=True, default=None),
        ),
        migrations.AlterField(
            model_name='account',
            name='account_balance',
            field=models.FloatField(default=0.0),
        ),
    ]