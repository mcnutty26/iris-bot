import os
import discord
import json
import asyncio
from utils.karma import karma_parse, karma_change
from utils.command import process_commands
from utils.gym import check_for_classes
from creds import CREDS
from models import db_session, User

token = CREDS['DISCORD_TOKEN']

client = discord.Client()

async def gym_check():
    await client.wait_until_ready()
    exercise_channel_id = 600743628356190214
    channel = client.get_channel(exercise_channel_id)
    while not client.is_closed():
        response = check_for_classes() 
        if not response == '':
            await channel.send(response)
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    # bot should not respond to itself
    if message.author == client.user:
        return

    author = message.author.id
    user = db_session.query(User).filter(User.uid == author).first()
    if not user:
        new_user = User(uid=author,admin=0)
        db_session.add(new_user)
        db_session.commit()

    # if message is a command, we want to do something with it
    if message.content.lower().startswith('iris ') or (message.content.startswith('!') and not message.content.startswith('!!') and not message.content.startswith('! ') and not (message.content.endswith('!') and message.content.startswith('!'))) or message.content.startswith(f'<@!{client.user.id}> '):
        reply = process_commands(db_session, message)
        if not reply == '':
            await message.channel.send(reply)
    # otherwise, it might contain karma so we should parse it for karma
    else:
        changes = karma_parse(message)
        if len(changes) > 0:
            reply = karma_change(db_session, author, changes)
            await message.channel.send(reply)

client.loop.create_task(gym_check())
client.run(token)
