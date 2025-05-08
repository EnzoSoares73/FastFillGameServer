from django.urls import re_path

from game_server.consumer import GameConsumer

urlpatterns = [
    re_path(r"game/$", GameConsumer.as_asgi()),
]