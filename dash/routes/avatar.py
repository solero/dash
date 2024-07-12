import asyncio
import io
import os

from PIL import Image
from sanic import Blueprint, response
from sanic.log import logger

from dash import app
from dash.data.penguin import Penguin

avatar = Blueprint('avatar', url_prefix='/avatar')

valid_sizes = [60, 88, 95, 120, 300, 600]
cache_expiry = 60 * 10

avatar_item_directory = os.path.abspath("./items")


@avatar.listener('before_server_start')
async def check_avatar_item_directory(app, loop):
    if not os.path.exists(avatar_item_directory):
        logger.warn((f'Avatar directory \'{avatar_item_directory}\' is missing! '
                     'Either download from https://icerink.solero.me/media1.clubpenguin.com/avatar/paper/ '
                     'or let wand mount the directory for you!'))


@avatar.get('/<penguin_id:int>')
async def get_avatar(request, penguin_id: int):
    background = request.args.get('photo', 'true')
    size = request.args.get('size', 120)
    if int(size) not in valid_sizes:
        return response.json({"message": 'Invalid size'}, status=400)

    image = await app.ctx.redis.get(f'{penguin_id}.{size}.avatar')

    if not image:
        clothing = await Penguin.select(
            'photo', 'color', 'head', 'face', 'body', 'neck', 'hand', 'feet'
        ).where(Penguin.id == penguin_id).gino.first()

        if clothing is None:
            return response.json({'message': 'Not found'}, status=404)

        clothing = list(clothing)

        if background != 'true':
            clothing.pop(0)

        loop = asyncio.get_event_loop()
        try:
            future = loop.run_in_executor(None, build_avatar, clothing, int(size))
            image = await asyncio.wait_for(future, timeout=5.0)

            await app.ctx.redis.setex(f'{penguin_id}.{size}.avatar', cache_expiry, image)
        except asyncio.TimeoutError:
            return response.json({"message": "Something has gone wrong."}, status=500)
    else:
        await app.ctx.redis.expire(f'{penguin_id}.{size}.avatar', cache_expiry)
    return response.raw(image, headers={'Content-type': 'image/png'})


def build_avatar(clothing, size):
    avatar_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    for item in filter(None, clothing):
        try:
            item_image = Image.open(f'{avatar_item_directory}/{size}/{item}.png', 'r')
            avatar_image.paste(item_image, (0, 0), item_image)
        except FileNotFoundError as e:
            logger.error(e)

    b = io.BytesIO()
    avatar_image.save(b, 'PNG')
    return b.getvalue()
