import django.db.models.deletion
import painel.models
from django.db import migrations, models
from painel import get_installed_themes
from painel.migrations import create_localhost_themes, create_localhost_contratante
    

class Migration(migrations.Migration):

    dependencies = [
        ("painel", "0021_dev_env"),
    ]

    operations = [
        migrations.RunPython(create_localhost_themes),
        migrations.RunPython(create_localhost_contratante),
    ]
