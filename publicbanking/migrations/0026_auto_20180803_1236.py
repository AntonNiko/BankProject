# Generated by Django 2.0.7 on 2018-08-03 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publicbanking', '0025_auto_20180803_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_type',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
