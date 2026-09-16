# core/serializers.py
from datetime import date
from rest_framework import serializers
from .models import Project, Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "project", "title", "description",
            "priority", "status", "due_date", "tags", "created_at",
        ]

    def validate_due_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("La fecha límite no puede ser en el pasado.")
        return value

    def validate(self, data):
        # Validación que involucra más de un campo
        if data.get("status") == "completada" and not data.get("due_date"):
            raise serializers.ValidationError(
                "No se puede marcar una tarea como completada sin fecha límite registrada."
            )
        # --- INICIO VALIDACIÓN TAREA ---
        #    Obtenemos el status enviado en los datos; si no viene en la petición,
        #    tomamos el status actual de la tarea desde self.instance.
        status = data.get("status") or (self.instance.status if self.instance else None)

        #    Obtenemos el proyecto asociado enviado en data; si no viene en la petición,
        #    recuperamos el proyecto que ya tenía asignado la tarea (self.instance.project).
        project = data.get("project") or (self.instance.project if self.instance else None)

        #    Comprobamos la condición: solo evaluamos si el status resultante es "en_progreso"
        #    y la tarea está vinculada a un proyecto.
        if status == "en_progreso" and project:
            #    Usamos el ORM a través de la relación inversa ('related_name="tasks"')
            #    para filtrar si existe al menos una tarea del proyecto con status "completada".
            has_completed_tasks = project.tasks.filter(status="completada").exists()

            #   Si la consulta devuelve False (no hay ninguna completada), lanzamos el error de validación.
            if not has_completed_tasks:
                raise serializers.ValidationError(
                    "Una tarea no puede estar en progreso si su proyecto no tiene ninguna tarea completada todavía."
                )
            
        return data


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "tasks", "created_at"]