# Generated by Django 2.0.7 on 2018-08-03 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publicbanking', '0027_auto_20180803_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='account_type',
        ),
        migrations.AddField(
            model_name='account',
            name='account_type',
            field=models.ManyToManyField(related_name='account_type', to='publicbanking.AccountType'),
        ),
    ]
