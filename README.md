# Fast Fill Game - Server Implementation

The server-side component for the Fast Fill Game, a competitive multiplayer game where players race to click squares faster than their opponents.

## 🚀 Quick Start

### Prerequisites

Docker and Docker Compose installed

Setup

1. Configure Environment

Create a ```.env``` file with the following variables:

```
SECRET_KEY=your_strong_secret_key_here
DEBUG=1  # Set to 0 in production
DJANGO_ALLOWED_HOSTS=http://0.0.0.0
```


Run the Server
Execute the following command:

```
docker-compose -f docker-compose.yml up --build
```