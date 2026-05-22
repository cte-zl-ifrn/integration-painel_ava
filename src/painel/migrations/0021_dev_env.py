from django.db import migrations

from painel.migrations import create_localhost_ambiente, create_localhost_themes


class Migration(migrations.Migration):

    dependencies = [
        ("painel", "0020_theme_apelido"),
    ]

    operations = [
        migrations.RunPython(create_localhost_themes),
        migrations.RunPython(create_localhost_ambiente),
    ]
