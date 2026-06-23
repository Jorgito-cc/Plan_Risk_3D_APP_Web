"""WebSocket Consumer para la colaboración en tiempo real del Editor 3D."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class EditorConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket para sincronizar movimientos de piezas 3D.

    Cada sala se identifica por un token_uuid. Los mensajes se
    retransmiten (broadcast) a todos los participantes de la sala
    excepto al emisor original.
    """

    async def connect(self):
        """Unirse a la sala de colaboración al conectar."""
        self.room_token = self.scope['url_route']['kwargs']['room_token']
        self.room_group_name = f'editor_{self.room_token}'

        # Extraer info del usuario de query params
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        params = dict(
            p.split('=') for p in query_string.split('&') if '=' in p
        )
        self.user_name = params.get('user', 'Anónimo')
        self.user_color = params.get('color', '#3B82F6')

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notificar a la sala que alguien se unió
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': self.user_name,
                'color': self.user_color,
                'channel': self.channel_name,
            }
        )

    async def disconnect(self, close_code):
        """Salir de la sala al desconectar."""
        # Notificar que el usuario se fue
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': self.user_name,
                'channel': self.channel_name,
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Recibir mensaje del cliente y retransmitir a la sala.

        Tipos de mensaje esperados:
        - mover: {accion: "mover", pieza_id: "...", posicion: {x, y, z}}
        - soltar: {accion: "soltar", pieza_id: "...", posicion: {x, y, z}}
        """
        data = json.loads(text_data)
        data['user'] = self.user_name
        data['color'] = self.user_color
        data['sender_channel'] = self.channel_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'piece_update',
                'message': data,
            }
        )

    # --- Handlers de eventos del grupo ---

    async def piece_update(self, event):
        """Retransmitir actualización de pieza a todos excepto el emisor."""
        message = event['message']

        # No reenviar al emisor original
        if message.get('sender_channel') == self.channel_name:
            return

        # Limpiar campo interno antes de enviar al cliente
        msg_to_send = {k: v for k, v in message.items() if k != 'sender_channel'}

        await self.send(text_data=json.dumps(msg_to_send))

    async def user_joined(self, event):
        """Notificar a todos que un usuario se unió."""
        await self.send(text_data=json.dumps({
            'accion': 'usuario_unido',
            'user': event['user'],
            'color': event['color'],
        }))

    async def user_left(self, event):
        """Notificar a todos que un usuario se fue."""
        await self.send(text_data=json.dumps({
            'accion': 'usuario_salio',
            'user': event['user'],
        }))
