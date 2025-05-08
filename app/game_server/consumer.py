import json
import random
import string
from collections import Counter, defaultdict

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
    rematch_requests = defaultdict(set)

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
            'color': assigned_color,
        }))

        if self.room_connection_counts[available_room_code] == 2:
            await self.channel_layer.group_send(
                available_room_code,
                {
                    'type': 'game_start',
                }
            )

            await self.init_game(available_room_code)

    async def init_game(self, available_room_code):
        self.rematch_requests[available_room_code] = set()

        self.games[available_room_code] = {}
        for i in range(board_size ** 2):
            self.games[available_room_code].update({i: None})

    async def disconnect(self, _):
        if hasattr(self, 'room_code'):
            await self.free_color()

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

    async def free_color(self):
        if self.room_code in self.player_colors:
            if self.channel_name in self.player_colors[self.room_code]:
                del self.player_colors[self.room_code][self.channel_name]

    async def receive(self, text_data=None, _=None):
        if self.games[self.room_code] is None:
            return

        try:
            data = json.loads(text_data)
            if hasattr(self, 'room_code'):
                await self.process_click(data)

                await self.process_rematch(data)


        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format',
                'type': 'error'
            }))

    async def process_rematch(self, data):
        if 'rematch' in data:
            self.rematch_requests[self.room_code].add(self.channel_name)

            agreed_players = len(self.rematch_requests[self.room_code])
            total_players = len(self.player_colors[self.room_code])

            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'rematch_update',
                    'requester': self.channel_name,
                    'agreed': agreed_players,
                    'total': total_players
                }
            )

            if agreed_players == total_players:
                await self.init_game(self.room_code)
                await self.channel_layer.group_send(
                    self.room_code,
                    {
                        'type': 'game_start'
                    }
                )



    async def process_click(self, data):
        if 'index' in data:
            event_position = self.games[self.room_code][int(data['index'])]
            if event_position is None:
                await self.fill_square(data)

                await self.determine_game_over()

    async def fill_square(self, data):
        self.games[self.room_code][int(data['index'])] = self.player_colors[self.room_code][self.channel_name]
        await self.channel_layer.group_send(
            self.room_code,
            {
                'type': 'action',
                'action': {
                    int(data['index']): self.player_colors[self.room_code][self.channel_name]}
            }
        )

    async def determine_game_over(self):
        occupied_positions = [color for color in self.games[self.room_code].values() if
                              color is not None]
        number_of_plays = len(occupied_positions)
        if number_of_plays == board_size ** 2:
            color_counts = Counter(occupied_positions)

            if color_counts['red'] > color_counts['blue']:
                winner = 'red'
            elif color_counts['blue'] > color_counts['red']:
                winner = 'blue'
            else:
                winner = 'tie'

            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'game_stop',
                    'result': winner
                }
            )

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
            'type': 'group_message',
            'message': event['message']
        }))

    async def action(self, event):
        await self.send(text_data=json.dumps({
            'type': 'action',
            'action': event['action']
        }))

    async def self_color(self, event):
        await self.send(text_data=json.dumps({
            'type': 'self_color',
            'color': event['color'],
        }))

    async def game_start(self, _):
        await self.send(text_data=json.dumps({
            'type': 'game_start'
        }))

    async def game_stop(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_stop',
            'result': event['result'],
        }))

    async def rematch_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'rematch_update',
            'requester': event['requester'],
            'agreed': event['agreed'],
            'total': event['total']
        }))