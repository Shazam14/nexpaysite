# Generated by Django 4.2 on 2023-04-30 00:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nexpay_forexapp', '0007_user_delete_customuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
