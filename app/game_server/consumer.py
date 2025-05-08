import json
import random
import string

from channels.generic.websocket import AsyncWebsocketConsumer

board_size = 4

def generate_random_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

class GameConsumer(AsyncWebsocketConsumer):
    room_connection_counts = dict()
    available_rooms = []
    player_colors = dict()
    games = dict()
    COLOR_CHOICES = ['red', 'blue']

    async def connect(self):
        await self.accept()

        if len(self.available_rooms) > 0:
            available_room_code = self.available_rooms.pop(0)
            self.room_connection_counts[available_room_code] = 2
        else:
            available_room_code = generate_random_code()
            self.available_rooms.append(available_room_code)
            self.room_connection_counts[available_room_code] = 1
            self.player_colors[available_room_code] = {}

        await self.channel_layer.group_add(
            available_room_code,
            self.channel_name
        )

        assigned_color = await self.assign_player_color(available_room_code, self.room_connection_counts[available_room_code])
        self.player_color = assigned_color

        self.room_code = available_room_code

        await self.send(text_data=json.dumps({
            'type': 'self_color',
            'message': f'You are connection #{self.room_connection_counts[available_room_code]} and have been added to the group {available_room_code}',
            'color': assigned_color,
        }))

        if self.room_connection_counts[available_room_code] == 2:
            room_colors = self.player_colors[available_room_code]
            await self.channel_layer.group_send(
                available_room_code,
                {
                    'type': 'room_colors',
                    'colors': room_colors,
                    'message': 'Room is now full! Game will now start.'
                }
            )

            await self.init_game(available_room_code)

    async def init_game(self, available_room_code):
        self.games[available_room_code] = {}
        for i in range(board_size ** 2):
            self.games[available_room_code].update({i: None})

    async def disconnect(self, close_code):
        if hasattr(self, 'room_code'):
            if self.room_code in self.player_colors:
                if self.channel_name in self.player_colors[self.room_code]:
                    del self.player_colors[self.room_code][self.channel_name]

            if self.room_code in self.room_connection_counts:
                self.room_connection_counts[self.room_code] -= 1

                if self.room_connection_counts[self.room_code] == 1:
                    self.available_rooms.append(self.room_code)
                    await self.channel_layer.group_send(
                        self.room_code,
                        {
                            'type': 'group_message',
                            'message': 'Player disconnected. Room is now available for another player.'
                        }
                    )

                elif self.room_connection_counts[self.room_code] <= 0:
                    del self.room_connection_counts[self.room_code]
                    if self.room_code in self.available_rooms:
                        self.available_rooms.remove(self.room_code)

    async def receive(self, text_data=None, bytes_data=None):
        if self.games[self.room_code] is None:
            return

        try:
            data = json.loads(text_data)
            if 'index' in data and hasattr(self, 'room_code'):
                    event_position = self.games[self.room_code][int(data['index'])];
                    if  event_position is None:
                        self.games[self.room_code][int(data['index'])] = self.player_colors[self.room_code][self.channel_name]

                        await self.channel_layer.group_send(
                            self.room_code,
                            {
                                'type': 'action',
                                'message': {
                                    int(data['index']): self.player_colors[self.room_code][self.channel_name]}
                            }
                        )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format',
                'type': 'error'
            }))

    async def assign_player_color(self, room_code, num_connections):
        if num_connections == 1:
            color = 'red'
        else:
            used_colors = set(self.player_colors[room_code].values())
            available_colors = [c for c in self.COLOR_CHOICES if c not in used_colors]
            color = available_colors[0]

        self.player_colors[room_code][self.channel_name] = color
        return color


    async def group_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    async def action(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    async def room_colors(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'colors': event['colors']
        }))

    async def self_color(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'color': event['color']
        }))