# core/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Project

 
 
class TaskNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]

        # 1. Consultar la BD de forma asíncrona
        project_exists = await database_sync_to_async(
            Project.objects.filter(id=self.project_id).exists
        )()

        # 2. Si el proyecto no existe, cerramos la conexión inmediatamente
        if not project_exists:
            await self.close()
            return

        self.group_name = f"project_{self.project_id}"

        # 3. Unirnos al grupo y aceptar la conexión
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Nos aseguramos de remover del grupo solo si llegó a crearse self.group_name
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({"echo": data}))

    async def task_notification(self, event):
        await self.send(text_data=json.dumps(event["payload"]))