# Generated by Django 2.0.5 on 2018-08-12 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publicbanking', '0032_auto_20180812_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='wiretransaction',
            name='transaction_destination_instNum',
            field=models.CharField(default='null', max_length=20),
            preserve_default=False,
        ),
    ]
