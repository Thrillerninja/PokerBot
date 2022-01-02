import discord
from discord.ext import commands
from discord.utils import get
import os
from PIL import Image
import numpy as np
import random
import operator
import asyncio

bot = commands.Bot(command_prefix="<", description="This is a Poker Bot")
client = discord.Client()

pokertisch = 925128488690782288      #id pokertisch
commands = 924987151211434059
global player
player = []
global playerlist
playerlist = []
global game_cards   #Kartendeck für dieses Spiel
game_cards = []
global game_state
game_state = 0
global mid
mid = []
hands = []
mid = []
min_bid = 1
reaction = False
raise_reaction = False
raise_reaction = False
max_raise = len(player)

global bidding_allowed
bidding_allowed = False
global current_bidder
current_bidder = 0

#Game_State = Aktuelle Stage
#0 = Ausgangszustand
#1 = Einladung (nach all in)
#2 = Kartenausgabe (nach letza go)
#3 
startmoney = 100
global cards  # Pik > Herz > Karo > Kreuz
money = {}                #Kontostand jedes Spielers
round_money = {}          #Gesetzter betrag jedes Spielers
backup_round_money = {}   #Gesetzter betrag jedes Spielers auf Null zurückgesetzt
pot = 0                   #Gesamtbetrag aller Gebote der an den Gewinner ausgezahlt wird
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
    global game_state       #game state management
    
    if message.author == client.user:
        return
#----------------------------------------------------------------------------------
# Runde erstellen und gegebenenfalls startmoney zuweisen
    if message.content.startswith('<create_Round'):
      if game_state == 0:       #correct game state reached?
        if  len(message.content.split(" ", 1)) >=2:
          value = message.content.split(" ", 1)[1]
          print(value) 
          global startmoney
          startmoney = int(value)

        await message.channel.send('Type <im in to enter')
        game_state = game_state + 1       #game state management
        

#Spieler können joinen
    if message.content.startswith('<im in'):
      if game_state == 1:       #correct game state reached?
        player.append(message.author)
        playerlist.append(message.author.name)
        money.update({str(message.author.name): startmoney})
        backup_round_money.update({str(message.author.name): 0})
        print(money) 
        await message.channel.send("Added " + str(message.author) + "!")

#test
    if message.content.startswith('<Hello'):
        await message.channel.send('Hello!')

#player ID's ausgeben
    if message.content.startswith('<players'):
        await message.channel.send(player)
#Gamestate zurücksetzen    
    if message.content.startswith('<reset'):
      game_state = 0
    
      
#Liste mit allen Spielern und dern Position in der Liste ausgeben      
    if message.content.startswith('<playerlist'):
      await message.channel.send('Playerlist:')
      await message.channel.send("---------------------------------------------------")
      for x in range(0, len(playerlist)):
        await message.channel.send(str(x+1) +". " + str(playerlist[x]))
      await message.channel.send("---------------------------------------------------")

#Eine Runde starten, wenn mindestens 2 Spieler dabei sind
    if message.content.startswith('<start_Round'):
      global current_bidder
      #game state management
      if game_state == 1:       #correct game state reached?
        if len(player) >= 1:
          game_cards = cards
          random.shuffle(game_cards) #Karten mischen
          ingame_players = playerlist
          global round_members
          round_members = ingame_players
          global potential_winners
          potetial_winners = ingame_players
          global round_money
          round_money = backup_round_money
          for x in range(0, len(player)):  
            user = player[x]
            img1 = Image.open(str(game_cards[0]) + ".png")
            img2 = Image.open(str(game_cards[1]) + ".png")
            blank_hand = Image.new('RGBA', (1000,726), 'white')
            blank_hand.paste(img1,(0,0,500,726))
            blank_hand.paste(img2,(500,0,1000,726))
            blank_hand.save("Temporary_Hand.png")
            await user.send(file=discord.File("Temporary_Hand.png")) #Karte 1 und 2 zusenden
            temporary_hand = []      #Karten, welche dem Spieler geschickt werden
            temporary_hand.append(game_cards[0])
            temporary_hand.append(game_cards[1])
            hands.append(temporary_hand) #Karten, welche dem Spieler geschickt werden
            game_cards  = np.delete(game_cards, [0]) #löschen der vergebenen Karten aus dem Stappel
            game_cards  = np.delete(game_cards, [0])  #array 1 kürzer
         
          #game_state erhöhen
          game_state = game_state + 1       #game state management
          print(hands)
          global bidding_allowed          
          channel = client.get_channel(pokertisch)
          await channel.send(str(round_members[current_bidder]) + " choose between *<raise Value <check and  <dodge*")

          bidding_allowed = True
          current_bidder = 0
        else:
          await message.channel.send("Waiting for " + str(1-len(player)) + " more Players")

    biddingloop(message)
    
    if current_bidder >= len(round_members) and bidding_allowed == True: #alle haben eine Aktion durchgeführt
      current_bidder = 0
    if reaction == True:
      current_bidder += 1
      channel = client.get_channel(pokertisch)
      print(current_bidder)
      await channel.send(str(round_members[current_bidder]) + " choose between *<raise Value <check and  <dodge*")
    if raise_reaction == True:
      current_bidder +=1
      channel = client.get_channel(pokertisch)
      print(current_bidder)
      print(raise_player)
      await channel.send(str(raise_player[current_bidder]) + " choose between *<raise Value <call and  <dodge*")
      

    
    
      


def global_raise():
  raise_player = round_members[current_bidder + 1:len(round_members)]
  raise_player.append(round_members[0:current_bidder - 1])                #Mitglieder, welche nacheinander erhöhen müssen
  print("Raise_Player in Methode:"+ str(raise_player))
  return raise_player

def biddingloop(message):
  global reaction
  global bidding_allowed
  global current_bidder
  global raise_reaction
  global raise_player
  if bidding_allowed == True and message.author.name == round_members[current_bidder]:
    reaction = False
    if message.content.startswith("<check"):
      reaction = True                        #end loop
    if message.content.startswith("<dodge"):
      round_members.remove(round_members[current_bidder])
      potential_winners.remove(round_members[current_bidder])
      reaction = True                        #end loop
    if message.content.startswith("<raise"):
      if  len(message.content.split(" ", 1)) == 2:
        global money_value
        money_value = message.content.split(" ", 1)[1]
        raise_reaction = True   
        raise_player = global_raise()  
        print("Raise_Player nach Methodenabruf:"+ str(raise_player))
        current_bidder = 0   
        bidding_allowed = False
      else:
        money_value = 1
        raise_reaction = True  
        raise_player = global_raise()     
        print("Raise_Player nach Methodenabruf:"+ str(raise_player))
        current_bidder = 0
        bidding_allowed = False  
      print(current_bidder)  
      round_money.update({str(round_members[current_bidder]):int(round_money[round_members[current_bidder]]) + int(money_value)})
      print(round_money)
  if raise_reaction == True and message.author.name == raise_player[current_bidder]: #Wenn jemand erhöht hat wird gefragt ob man mitgehen, rausgehen oder weiter erhöhen will
    raise_reaction = False
    if message.content.startstwith("<call"):
      max_key = max(round_money.iteritems(), key=operator.itemgetter(1))[0]
      round_money.update({str(raise_player[current_bidder]):int(round_money[max_key])})
      raise_reaction = True
      print(round_money)

      

    

    



      




      
  

  



          # #Anfang Gebote
          # #-------------------------------------------------------
          # for x in round_members:
          #   channel = client.get_channel(pokertisch)
          #   await channel.send(str(x) + " choose between *<raise Value <check and  <dodge*")
          #   reaction = False
          #   while reaction == False:
          #     print("Im in")
          #     print("Message: ", message)
          #     if message.author.name == x:
          #       if message.content.startswith("<check"):
          #         reaction = True                        #end loop
          #       if message.content.startswith("<dodge"):
          #         round_members.remove(round_members[x])<
          #         reaction = True                        #end loop
          #       if message.content.startswith("<raise"):
          #         if  len(message.content.split(" ", 1)) ==2:
          #           global money_value
          #           money_value = message.content.split(" ", 1)[1]
          #           reaction = True                        #end loop
          #         else:
          #           money_value = 1
          #         round_money.update({str(x):round_money[x] + money_value})
          #         reaction = True                        #end loop
          #       print(round_money)
                  
          #     else: 
          #       print(message.author.name)
          #       print(x)
                  















      
        


        #mid.append(game_cards[0,1,2])     
        #channel = client.get_channel(pokertisch)
        #channel.send

client.run(os.getenv("TOKEN"))
#































