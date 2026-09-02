# Módulos estándar de Python para procesar diferentes formatos de archivos
import csv                             # Para leer archivos separados por comas (.csv)
import json                            # Para leer y decodificar archivos JSON (.json)
import xml.etree.ElementTree as ET     # Para parsear y extraer etiquetas de archivos XML (.xml)

# Clases base de Django
from django.core.management.base import BaseCommand  # Permite crear comandos personalizados para 'python manage.py <comando>'
from core.models import Task                         # Modelo de base de datos donde se guardarán los registros


class Command(BaseCommand):
    # Texto de ayuda visible al ejecutar: python manage.py <comando> --help
    help = "Importa tareas desde múltiples proveedores (JSON, CSV, XML)"

    def handle(self, *args, **options):
        """Método principal que Django ejecuta al correr el comando."""
        total = 0  # Acumulador para contar cuántas tareas se importaron con éxito
        
        # Procesa secuencialmente cada uno de los tres orígenes de datos
        total += self._import_json("data/tasks_provider_a.json", source="proveedor_a")
        total += self._import_csv("data/tasks_provider_b.csv", source="proveedor_b")
        total += self._import_xml("data/tasks_provider_c.xml", source="proveedor_c")
        
        # Imprime un mensaje en verde (SUCCESS) en la terminal con el total consolidado
        self.stdout.write(self.style.SUCCESS(f"Importación finalizada: {total} tareas cargadas"))

    def _import_json(self, path, source):
        """Lee un archivo JSON, recorre su lista de elementos y los manda a guardar."""
        count = 0
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)  # Transforma el texto JSON en una lista de diccionarios de Python
            for item in data:
                self._crear_task(item, source)  # Guarda cada registro en la BD
                count += 1
        # Captura errores si el archivo no existe o si el JSON está mal formateado
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.stderr.write(self.style.ERROR(f"Error importando {path}: {e}"))
        return count

    def _import_csv(self, path, source):
        """Lee un archivo CSV fila por fila mapeando cabeceras como claves de diccionario."""
        count = 0
        try:
            with open(path, encoding="utf-8") as f:
                # DictReader usa la primera fila como nombres de campos para cada diccionario
                reader = csv.DictReader(f)
                for row in reader:
                    self._crear_task(row, source)
                    count += 1
        # Captura el error si el archivo CSV no se encuentra
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"Error importando {path}: {e}"))
        return count

    def _import_xml(self, path, source):
        """Parsea un archivo XML y extrae el texto de las etiquetas hijas de cada <task>."""
        count = 0
        try:
            tree = ET.parse(path)  # Analiza el árbol del documento XML
            # Busca todas las etiquetas <task> bajo el nodo raíz
            for task_el in tree.getroot().findall("task"):
                # Arma un diccionario equivalente con el contenido textual de cada etiqueta interna
                item = {
                    "title": task_el.find("title").text,
                    "priority": task_el.find("priority").text,
                    "status": task_el.find("status").text,
                }
                self._crear_task(item, source)
                count += 1
        # Captura errores si el archivo no existe o si las etiquetas XML no cierran bien
        except (FileNotFoundError, ET.ParseError) as e:
            self.stderr.write(self.style.ERROR(f"Error importando {path}: {e}"))
        return count

    def _crear_task(self, item, source):
        """Valida y realiza el INSERT en la base de datos usando el ORM de Django."""
        # Validación: descarta el registro si viene sin título o vacío
        if not item.get("title"):
            self.stderr.write(self.style.WARNING("Item sin título, se ignora"))
            return
        
        # Crea y persiste la fila en la tabla de Task
        Task.objects.create(
            title=item["title"],
            priority=item.get("priority", "media"),    # Si no tiene 'priority', asigna "media" por defecto
            status=item.get("status", "pendiente"),     # Si no tiene 'status', asigna "pendiente" por defecto
            source=source,                              # Identifica qué proveedor envió este registro
        )

