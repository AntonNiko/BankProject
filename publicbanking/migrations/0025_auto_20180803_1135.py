# Generated by Django 2.0.7 on 2018-08-03 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publicbanking', '0024_client_client_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='client_city',
            field=models.CharField(max_length=100),
        ),
    ]
