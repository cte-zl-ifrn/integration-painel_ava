import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined"),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that IFRN-id already exists."},
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="IFRN-id",
                    ),
                ),
                (
                    "nome_civil",
                    models.CharField(max_length=255, verbose_name="nome civil"),
                ),
                (
                    "nome_social",
                    models.CharField(max_length=255, verbose_name="nome social"),
                ),
                (
                    "nome_apresentacao",
                    models.CharField(max_length=255, verbose_name="nome de apresentação"),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("I", "Incerto"),
                            ("S", "Servidor"),
                            ("T", "Técnico"),
                            ("D", "Docente"),
                            ("E", "Estagiário"),
                            ("P", "Prestador"),
                            ("A", "Aluno"),
                        ],
                        max_length=255,
                        verbose_name="tipo",
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, null=True, verbose_name="e-Mail prefernical"),
                ),
                (
                    "email_secundario",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        verbose_name="e-Mail pessoal",
                    ),
                ),
                (
                    "email_corporativo",
                    models.EmailField(blank=True, max_length=254, verbose_name="e-Mail corporativo"),
                ),
                (
                    "email_escolar",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        verbose_name="e-Mail escolar",
                    ),
                ),
                (
                    "email_academico",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        verbose_name="e-Mail academico",
                    ),
                ),
                (
                    "first_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="first login"),
                ),
            ],
            options={
                "verbose_name": "usuário",
                "verbose_name_plural": "usuários",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Grupo",
            fields=[
                (
                    "group_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="auth.group",
                    ),
                ),
            ],
            bases=("auth.group",),
            managers=[
                ("objects", django.contrib.auth.models.GroupManager()),
            ],
        ),
    ]
