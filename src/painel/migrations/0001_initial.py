import re

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ambiente",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sigla",
                    models.CharField(max_length=255, unique=True, verbose_name="sigla do ambiente"),
                ),
                (
                    "nome",
                    models.CharField(max_length=255, verbose_name="nome do ambiente"),
                ),
                ("url", models.CharField(max_length=255, verbose_name="URL")),
                ("token", models.CharField(max_length=255, verbose_name="token")),
                ("active", models.BooleanField(default=True, verbose_name="ativo?")),
            ],
            options={
                "verbose_name": "ambiente",
                "verbose_name_plural": "ambientes",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="Campus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suap_id",
                    models.CharField(max_length=255, unique=True, verbose_name="ID do campus no SUAP"),
                ),
                (
                    "sigla",
                    models.CharField(max_length=255, unique=True, verbose_name="sigla do campus"),
                ),
                (
                    "descricao",
                    models.CharField(max_length=255, verbose_name="descrição"),
                ),
                ("active", models.BooleanField(verbose_name="ativo?")),
                (
                    "ambiente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="painel.ambiente",
                    ),
                ),
            ],
            options={
                "verbose_name": "campus",
                "verbose_name_plural": "campi",
                "ordering": ["sigla"],
            },
        ),
        migrations.CreateModel(
            name="Componente",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suap_id",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        verbose_name="ID do componente no SUAP",
                    ),
                ),
                (
                    "sigla",
                    models.CharField(max_length=255, unique=True, verbose_name="sigla do componente"),
                ),
                (
                    "descricao",
                    models.CharField(max_length=512, verbose_name="descrição"),
                ),
                (
                    "descricao_historico",
                    models.CharField(max_length=512, verbose_name="descrição no histórico"),
                ),
                (
                    "periodo",
                    models.IntegerField(blank=True, null=True, verbose_name="período"),
                ),
                (
                    "tipo",
                    models.IntegerField(blank=True, null=True, verbose_name="tipo"),
                ),
                (
                    "optativo",
                    models.BooleanField(blank=True, null=True, verbose_name="optativo"),
                ),
                (
                    "qtd_avaliacoes",
                    models.IntegerField(blank=True, null=True, verbose_name="qtd. avalições"),
                ),
            ],
            options={
                "verbose_name": "componente",
                "verbose_name_plural": "componentes",
                "ordering": ["sigla"],
            },
        ),
        migrations.CreateModel(
            name="Curso",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suap_id",
                    models.CharField(max_length=255, unique=True, verbose_name="ID do curso no SUAP"),
                ),
                (
                    "codigo",
                    models.CharField(max_length=255, unique=True, verbose_name="código do curso"),
                ),
                (
                    "nome",
                    models.CharField(max_length=255, verbose_name="nome do curso"),
                ),
                (
                    "descricao",
                    models.CharField(max_length=255, verbose_name="descrição"),
                ),
            ],
            options={
                "verbose_name": "curso",
                "verbose_name_plural": "cursos",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="Diario",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suap_id",
                    models.CharField(max_length=255, unique=True, verbose_name="ID do diário no SUAP"),
                ),
                (
                    "codigo",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("(\\d{5}\\.\\d\\.\\d{5}\\...)\\.(.*\\..*)")
                            )
                        ],
                        verbose_name="código do diário",
                    ),
                ),
                ("situacao", models.CharField(max_length=255, verbose_name="situação")),
                (
                    "descricao",
                    models.CharField(max_length=255, verbose_name="descrição"),
                ),
                (
                    "descricao_historico",
                    models.CharField(max_length=255, verbose_name="descrição no histórico"),
                ),
                (
                    "componente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="painel.componente",
                        verbose_name="componente",
                    ),
                ),
            ],
            options={
                "verbose_name": "diário",
                "verbose_name_plural": "diários",
                "ordering": ["codigo"],
            },
        ),
        migrations.CreateModel(
            name="Polo",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suap_id",
                    models.CharField(max_length=255, unique=True, verbose_name="ID do pólo no SUAP"),
                ),
                (
                    "nome",
                    models.CharField(max_length=255, unique=True, verbose_name="nome do pólo"),
                ),
            ],
            options={
                "verbose_name": "pólo",
                "verbose_name_plural": "pólos",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="Turma",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suap_id",
                    models.CharField(max_length=255, unique=True, verbose_name="ID da turma no SUAP"),
                ),
                (
                    "codigo",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(re.compile("(\\d{5})\\.(\\d)\\.(\\d{5})\\.(..)"))
                        ],
                        verbose_name="código da turma",
                    ),
                ),
                ("ano_mes", models.SmallIntegerField(verbose_name="ano/mês")),
                ("periodo", models.SmallIntegerField(verbose_name="período")),
                (
                    "sigla",
                    models.CharField(max_length=8, verbose_name="sigla da turma"),
                ),
                (
                    "turno",
                    models.CharField(
                        choices=[
                            ("N", "Noturno"),
                            ("V", "Vespertino"),
                            ("M", "Matutino"),
                            ("E", "EAD"),
                            ("D", "Diurno"),
                            ("I", "Integral"),
                            ("_", "Desconhecido"),
                        ],
                        max_length=1,
                        verbose_name="turno",
                    ),
                ),
                (
                    "campus",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="painel.campus",
                        verbose_name="campus",
                    ),
                ),
                (
                    "curso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="painel.curso",
                        verbose_name="curso",
                    ),
                ),
            ],
            options={
                "verbose_name": "turma",
                "verbose_name_plural": "turmas",
                "ordering": ["codigo"],
            },
        ),
        migrations.CreateModel(
            name="Inscricao",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "papel",
                    models.CharField(
                        choices=[
                            ("A", "Aluno"),
                            ("P", "Professor"),
                            ("R", "Tutor remoto"),
                        ],
                        max_length=1,
                        verbose_name="papel",
                    ),
                ),
                ("active", models.BooleanField(verbose_name="ativo?")),
                (
                    "diario",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="painel.diario"),
                ),
                (
                    "polo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="painel.polo",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "inscrição",
                "verbose_name_plural": "inscrições",
                "ordering": ["diario", "usuario"],
            },
        ),
        migrations.AddField(
            model_name="diario",
            name="turma",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="painel.turma",
                verbose_name="turma",
            ),
        ),
    ]
