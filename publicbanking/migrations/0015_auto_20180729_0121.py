# Generated by Django 2.0.7 on 2018-07-29 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publicbanking', '0014_client'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='account_holder',
        ),
        migrations.AddField(
            model_name='account',
            name='account_holder',
            field=models.ManyToManyField(to='publicbanking.Client'),
        ),
    ]
