from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_reviewrating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewrating',
            name='user',
        ),
    ]
