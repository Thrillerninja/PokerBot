import discord
from discord.ext import commands
from discord.utils import get
import os
import numpy as np
import random

bot = commands.Bot(command_prefix="<", description="This is a Poker Bot")
client = discord.Client()

global player
player = []
global playerlist
playerlist = []
global game_cards   #Kartendeck für dieses Spiel
game_cards = []
global game_state
game_state = 0
#Game_State = Aktuelle Stage
#0 = Ausgangszustand
#1 = Einladung (nach all in)
#2 = Kartenausgabe (nach letza go)
#3 

global cards  # Pik > Herz > Karo > Kreuz
cards = [
    "1-2",  #Kreuz = 2
    "1-3",  #Kreuz = 3
    "1-4",  #Kreuz = 4 
    "1-5",  #Kreuz = 5
    "1-6",  #Kreuz = 6
    "1-7",  #Kreuz = 7
    "1-8",  #Kreuz = 8
    "1-9",  #Kreuz = 9
    "1-10", #Kreuz = 10
    "1-11", #Kreuz = Bube
    "1-12", #Kreuz = Dame
    "1-13", #Kreuz = König
    "1-14", #Kreuz = Ass
    "2-2",  #Karo = 2
    "2-3",  #Karo = 3
    "2-4",  #Karo = 4
    "2-5",  #Karo = 5
    "2-6",  #Karo = 6
    "2-7",  #Karo = 7
    "2-8",  #Karo = 8
    "2-9",  #Karo = 9
    "2-10", #Karo = 10
    "2-11", #Karo = Bube
    "2-12", #Karo = Dame
    "2-13", #Karo = König
    "2-14", #Karo = Ass
    "3-2",  #Herz = 2
    "3-3",  #Herz = 3
    "3-4",  #Herz = 4
    "3-5",  #Herz = 5
    "3-6",  #Herz = 6
    "3-7",  #Herz = 7
    "3-8",  #Herz = 8
    "3-9",  #Herz = 9
    "3-10", #Herz = 10
    "3-11", #Herz = Bube
    "3-12", #Herz = Dame
    "3-13", #Herz = König
    "3-14", #Herz = Ass
    "4-2",  #Pik = 2
    "4-3",  #Pik = 3
    "4-4",  #Pik = 4
    "4-5",  #Pik = 5
    "4-6",  #Pik = 6
    "4-7",  #Pik = 7
    "4-8",  #Pik = 8
    "4-9",  #Pik = 9
    "4-10", #Pik = 10
    "4-11", #Pik = Bube
    "4-12", #Pik = Dame
    "4-13", #Pik = König
    "4-14", #Pik = Ass
]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name='Poker'))


@client.event
async def on_message(message):
    global player
    global playerlist
    if message.author == client.user:
        return

    if message.content.startswith('<all in'):
      global game_state       #game state management
      if game_state == 0:       #correct game state reached?
        await message.channel.send('Type <im in to enter')
        game_state = game_state + 1       #game state management

    if message.content.startswith('<im in'):
        player.append(message.author)
        playerlist.append(message.author.name)
        await message.channel.send("Added " + str(message.author) + "!")


    if message.content.startswith('<Hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('<players'):
        await message.channel.send(player)
        
    if message.content.startswith('<playerlist'):
      await message.channel.send('Playerlist:')
      await message.channel.send("---------------------------------------------------")
      for x in range(0, len(playerlist)):
        await message.channel.send(str(x+1) +". " + str(playerlist[x]))
      await message.channel.send("---------------------------------------------------")

    if message.content.startswith('<letsa go'):
      global game_state       #game state management
      if game_state == 1:       #correct game state reached?
        game_cards = cards
        random.shuffle(game_cards)
        print(game_cards)
        for x in range(0, len(player)):
          user = player[x]
          print(game_cards[0])
          print(game_cards[1])
          await user.send(str(game_cards[0])) #Karte 1 zusenden
          await user.send(str(game_cards[1])) #Karte 2 zusenden
          game_cards  = np.delete(game_cards, [0])
          game_cards  = np.delete(game_cards, [0])  #array 1 kürzer

        #game_state erhöhen
        game_state = game_state + 1       #game state management
        print(game_cards)

        


client.run(os.getenv("TOKEN"))
#































