# core/migrations/0014_horariodisponible.py
from django.db import migrations, models
import datetime

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS `horarios_disponibles` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `hora` TIME NOT NULL,
  `activa` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_hora` (`hora`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
"""

def seed_horarios(apps, schema_editor):
    HorarioDisponible = apps.get_model("core", "HorarioDisponible")
    base = [
        ("09:00:00", "9:00 AM"),
        ("12:00:00", "12:00 PM"),
        ("16:00:00", "4:00 PM"),
        ("19:00:00", "7:00 PM"),
    ]
    for hhmmss, label in base:
        h = datetime.datetime.strptime(hhmmss, "%H:%M:%S").time()
        HorarioDisponible.objects.get_or_create(
            hora=h, defaults={"etiqueta": label, "activa": True}
        )

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_alter_categoria_options_remove_categoria_created_at_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunSQL(CREATE_SQL)],
            state_operations=[
                migrations.CreateModel(
                    name="HorarioDisponible",
                    fields=[
                        ("id", models.AutoField(primary_key=True, serialize=False)),
                        ("hora", models.TimeField(unique=True)),
                        ("activa", models.BooleanField(default=True)),
                    ],
                    options={
                        "db_table": "horarios_disponibles",
                        "ordering": ["hora"],
                    },
                ),
            ],
        ),
        migrations.RunPython(seed_horarios, migrations.RunPython.noop),
    ]