# Generated by Django 5.1.6 on 2025-02-23 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='users_pfp/'),
        ),
    ]
