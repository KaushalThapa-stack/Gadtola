from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_rename_image_name_variation_image_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variation',
            name='variation_value',
        ),
    ]
