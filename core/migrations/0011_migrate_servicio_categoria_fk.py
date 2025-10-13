# core/migrations/0011_migrate_servicio_categoria_fk.py
from django.db import migrations

# Esquema compatible con 0010 (BigAutoField -> BIGINT, slug único y created_at con default)
CREATE_CATEGORIAS_SQL = """
CREATE TABLE IF NOT EXISTS `categorias` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(64) NOT NULL UNIQUE,
  `activa` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

BASE_CATS = [
    'Sin asignar',
]

def ensure_categorias_table(apps, schema_editor):
    # Si 0010 está marcada pero la tabla no existe, la creamos aquí.
    existing = set(schema_editor.connection.introspection.table_names())
    if 'categorias' not in existing:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(CREATE_CATEGORIAS_SQL)

def seed_categorias(apps, schema_editor):
    Categoria = apps.get_model('core', 'Categoria')
    for nombre in BASE_CATS:
        Categoria.objects.get_or_create(nombre=nombre, defaults={'activa': True})

def migrate_servicios_categoria(apps, schema_editor):
    """
    Solo si aún existiera un campo 'categoria' antiguo tipo char en la DB (defensa).
    Si ya es ForeignKey (como define 0010), esto no hace nada.
    """
    from django.db.models import ForeignKey
    Servicio = apps.get_model('core', 'Servicio')
    Categoria = apps.get_model('core', 'Categoria')

    # ¿'categoria' es FK ya?
    field = Servicio._meta.get_field('categoria')
    if isinstance(field, ForeignKey):
        return

    map_code = {
        '?': 'Sin asignar',
        None: 'Sin asignar'
    }
    cats = {c.nombre: c for c in Categoria.objects.all()}
    for s in Servicio.objects.all():
        nombre = map_code.get(getattr(s, 'categoria', None), 'Sin asignar')
        s.categoria = cats.get(nombre)
        s.save(update_fields=['categoria'])

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_categoria_alter_servicio_precio_and_more'),
    ]
    operations = [
        migrations.RunPython(ensure_categorias_table, migrations.RunPython.noop),
        migrations.RunPython(seed_categorias, migrations.RunPython.noop),
        migrations.RunPython(migrate_servicios_categoria, migrations.RunPython.noop),
    ]