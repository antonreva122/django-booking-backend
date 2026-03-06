# Generated migration for adding profile_image field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.URLField(blank=True, help_text='Cloudinary image URL', max_length=500, null=True),
        ),
    ]
