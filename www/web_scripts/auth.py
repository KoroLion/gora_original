import asyncio
from aiohttp import web
import json

async def handle(request):
    login = request.match_info.get('login', None)
    password_hash = request.match_info.get('password_hash', None)

    try:
        index = open("index.html", 'rb')
        content = index.read()
    except FileNotFoundError:
        content = json.dumps(login + password_hash).encode()

    return web.Response(body=content, content_type='text/html')

app = web.Application()
app["sockets"] = []

app.router.add_route('GET', '/{login}/{password_hash}', handle)
app.router.add_route('GET', '/', handle)

web.run_app(app)
