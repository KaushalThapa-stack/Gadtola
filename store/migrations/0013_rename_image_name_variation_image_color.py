from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_productimage_id_alter_variationimage_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variationimage',
            old_name='image_name',
            new_name='image_color',
        ),
        migrations.AlterField(
            model_name='variationimage',
            name='image_color',
            field=models.CharField(help_text="e.g., 'Front View', 'Side View' - for this color variation", max_length=200),
        ),
    ]
