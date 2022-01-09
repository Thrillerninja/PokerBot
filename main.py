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
ranking = []    #Liste, welche am Ende ausgegeben werden soll um zu sehen wer am besten war
global mid
mid = []      #Gemeinschaftskarten
hands = []    #Handkarten
small_blind = 1
min_bid = 1
reaction = False
raise_reaction = False
max_raise = len(player)
High_Bidd_Error = False
NOT_INT_DATATYPE = False

global bidding_allowed
bidding_allowed = False     #nur True wenn man nach dem umdeken von Karten wieder bieten darf
raise_allowed = False       #nur True wenn erhöht wurde und die restlicen Spieler wählen müssen wie sie reagieren
global current_bidder
current_bidder = 0

#Game_State = Aktuelle Stage
#0 = Ausgangszustand
#1 = Einladung (nach create)
#2 = Kartenausgabe (nach start)
#3 = 1. 3 Karten werden aufgedeckt
#4 = 4. Karte wird aufgedeckt
#5 = 5. Karte wird aufgedeckt
#6 = Auflösung 
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
    
    channel = client.get_channel(pokertisch)
    if message.channel == channel:
      await message.channel.purge(limit = 1)
#----------------------------------------------------------------------------------
# Runde erstellen und gegebenenfalls startmoney zuweisen
    if message.content.startswith('<create_Round') or message.content.startswith('<c'):
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
      if game_state == 1: 
        if message.author not in player:      #correct game state reached?
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
    if message.content.startswith('<start_Round') or message.content.startswith('<s'):
      global current_bidder
      global round_members
      global mid
      #game state management
      if game_state == 1:       #correct game state reached?
        if len(player) >= 1:
          #Pokertisch clearen
          channel = client.get_channel(pokertisch)
          await channel.purge(limit = 50)

          #Aussortieren, wer sich den smallblind nicht leisten kann
          for i in range(0,len(playerlist)):
            player_value = money[playerlist[i]]
            if player_value < small_blind:
              ranking.append(playerlist[i])
              playerlist.remove(playerlist[i]) 
              player.delete(playerlist.index(playerlist[i]))
              print("Removed ",str(playerlist[i]),"from the Game")
              channel = client.get_channel(pokertisch)
              await channel.send("Removed ",str(playerlist[i]),"from the Game")
              

          game_cards = cards[:]
          random.shuffle(game_cards) #Karten mischen
          ingame_players = playerlist[:]
          global round_members
          round_members = ingame_players[:]
          global potential_winners
          potential_winners = ingame_players[:]
          print("Potential_Winners: " + str(potential_winners))
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
          
          #mid vergeben (Karten in der Mitte) und mid_pic senden
          for y in range(5):
            mid.append(game_cards[0])
            game_cards = np.delete(game_cards, [0])
          mid_pic = Image.new('RGBA', (2500,726), 'white')
          global card_back
          card_back = Image.open("card_back.png")
          mid_pic.paste(card_back,(0,0,500,726))
          mid_pic.paste(card_back,(500,0,1000,726))
          mid_pic.paste(card_back,(1000,0,1500,726))
          mid_pic.paste(card_back,(1500,0,2000,726))
          mid_pic.paste(card_back,(2000,0,2500,726))
          mid_pic.save("mid_pic.png")
          channel = client.get_channel(pokertisch)
          await channel.send(file=discord.File("mid_pic.png"))

        
        

          #Startgebot für jeden Spieler Einsetzen 
          for i in range(0,len(round_members)):
            round_money.update({str(round_members[i]):int(small_blind)})
            money.update({str(round_members[i]):int(money[round_members[i]]) - int(small_blind)})
        


          #game_state erhöhen
          game_state = game_state + 1       #game state management
          print(hands)
          global bidding_allowed          
          channel = client.get_channel(pokertisch)
          await channel.send(str(round_members[current_bidder]) + " choose between *<raise Value <check and  <fold*")
          print("Money: " + str(money))

          bidding_allowed = True
          current_bidder = 0
        else:
          await message.channel.send("Waiting for " + str(1-len(player)) + " more Players")

    biddingloop(message)
    raise_loop(message)
    global raise_reaction
    global High_Bidd_Error
    global NOT_INT_DATATYPE
    global reaction
     
  #Bidd   
     #Wenn alle gecheckt oder gefolded haben soll die Schleife abgebrochen werden
    if game_state >= 2 and current_bidder >= len(round_members) and bidding_allowed == True: #alle haben eine Aktion durchgeführt
      current_bidder = 0
      bidding_allowed = False
      reaction = False
      game_state +=1
      channel = client.get_channel(pokertisch)
      await channel.purge(limit = 1)
      await channel.send("This Biddinground is over. You can flip the next card(s) with *<next_card*.")
    #Nachricht wer als nächtes am Zug ist
    if reaction == True:
      #current_bidder += 1
      channel = client.get_channel(pokertisch)
      print(current_bidder)
      await channel.purge(limit = 1)
      await channel.send(str(round_members[current_bidder]) + " choose between *<raise Value <check and  <all_in*")
      print("Money: " + str(money))
    
  #Raise  
    #Wenn alle gefragt werden soll die Schleife abgebrochen werden
    if raise_reaction == True and current_bidder > len(raise_player) - 1:
      #global raise_reaction
      global raise_allowed
      raise_reaction = False
      raise_allowed = False
      game_state +=1
      channel = client.get_channel(pokertisch)
      await channel.purge(limit = 1)
      await channel.send("This Biddinground is over. You can flip the next card(s) with *<next_card*.")
    #Nachricht wer als nächtes am Zug ist
    if raise_reaction == True and raise_allowed == True : #message.author == raise_player[current_bidder + 1]
      if current_bidder >= 0:  
        #current_bidder +=1
        channel = client.get_channel(pokertisch)
        print(current_bidder)
        print("Raise_Player:" + str(raise_player))
        await channel.purge(limit = 1)
        await channel.send(str(raise_player[current_bidder]) + " choose between *<raise Value <call <fold and <all_in*")
        print("Money: " + str(money))

      if current_bidder == -1:
        #current_bidder +=1
        channel = client.get_channel(pokertisch)
        print(current_bidder)
        print("Raise_Player:" + str(raise_player))
        channel = client.get_channel(pokertisch)
        await channel.purge(limit = 1)
        await channel.send(str(raise_player[current_bidder + 1]) + " choose between *<raise Value <call <fold and <all_in*")
        print("Money: " + str(money))


    #Gewinn durch das verlassen aller Spieler außer einem 
    if game_state >= 2 and len(potential_winners) == 1:
      print(str(potential_winners[0]) + " won the Game")
      print(str(potential_winners))

    #Error's    
    #-------------------------------------------------------------------------
    if High_Bidd_Error == True:
      channel = client.get_channel(pokertisch)
      await channel.purge(limit = 1)
      await channel.send(str(round_members[current_bidder] + "your balance is: " + str(money[round_members[current_bidder]]) + " . You can *<raise* with a lower *Value* or go *<all in* instead."))
      High_Bidd_Error = False

    if NOT_INT_DATATYPE == True:
      channel = client.get_channel(pokertisch)
      await channel.send("Gib gefälligst eine zahl an du Idiot!")
      NOT_INT_DATATYPE = False
        
  #First 3 Cards
  #--------------------------------------------------
    if message.content.startswith("<next_card") or message.content.startswith("<n") and game_state == 3:
      channel = client.get_channel(pokertisch)
      await channel.purge(limit = 50)
      mid_pic = Image.new('RGBA', (2500,726), 'white')
      x = 0
      y = 500
      for i in range(0, 3):
        img = Image.open(str(mid[i]) + ".png")
        mid_pic.paste(img,(x,0,y,726))
        x += 500
        y+= 500
      mid_pic.paste(card_back,(1500,0,2000,726))
      mid_pic.paste(card_back,(2000,0,2500,726))
      mid_pic.save("mid_pic.png")
      channel = client.get_channel(pokertisch)
      await channel.send(file=discord.File("mid_pic.png"))
      bidding_allowed = True
      current_bidder = 0
      reaction = False
      await channel.send(str(round_members[current_bidder]) + " choose between *<raise Value <check and  <fold*")
  
  #4. Card
  #-----------------------------------------
    if message.content.startswith("<next_card") or message.content.startswith("<n") and game_state == 4:
      channel = client.get_channel(pokertisch)
      await channel.purge(limit = 50)
      mid_pic = Image.new('RGBA', (2500,726), 'white')
      x = 0
      y = 500
      for i in range(0, 4):
        img = Image.open(str(mid[i]) + ".png")
        mid_pic.paste(img,(x,0,y,726))
        x += 500
        y+= 500 
      mid_pic.paste(card_back,(2000,0,2500,726))
      mid_pic.save("mid_pic.png")
      channel = client.get_channel(pokertisch)
      await channel.send(file=discord.File("mid_pic.png"))
      bidding_allowed = True
      current_bidder = 0
      reaction = False
      await channel.send(str(round_members[current_bidder]) + " choose between *<raise Value <check and  <fold*")

  #5. Card
  #-----------------------------------------
    if message.content.startswith("<next_card") or message.content.startswith("<n") and game_state == 5:
      channel = client.get_channel(pokertisch)
      await channel.purge(limit = 50)
      mid_pic = Image.new('RGBA', (2500,726), 'white')
      x = 0
      y = 500
      for i in range(0, 5):
        img = Image.open(str(mid[i]) + ".png")
        mid_pic.paste(img,(x,0,y,726))
        x += 500
        y+= 500 
      mid_pic.save("mid_pic.png")
      channel = client.get_channel(pokertisch)
      await channel.send(file=discord.File("mid_pic.png"))
      reaction = False
    #Auswertung der Spielerhände um Gewinner zu ermitteln 
      winners = auswertung()
     
      


def global_raise(all):
  if raise_allowed == False:
    global raise_player
    raise_player = round_members[current_bidder + all:len(round_members)] #fügt die Mitglieder hinter dem aktuellen Bidder in eine Liste ein
    for x in range(0, current_bidder -(1-all)):        #fügt die Mitglieder vor dem aktuellen Bidder hinter den anderen ein 
      raise_player.append(round_members[x])
    print("Raise_Player in Methode:"+ str(raise_player))
    return raise_player  #Gibt alle Mitglieder aus, welche nacheinander erhöhen müssen
  if raise_allowed == True:
    global indice
    indice = round_members.index(raise_player[current_bidder])
    print("Indicie: " + str(indice))
    raise_player = round_members[indice + 1:len(round_members)] #fügt die Mitglieder hinter dem aktuellen Bidder in eine Liste ein
    for x in range(0, indice):        #fügt die Mitglieder vor dem aktuellen Bidder hinter den anderen ein 
      raise_player.append(round_members[x])
    print("Raise_Player in Methode:"+ str(raise_player))
    return raise_player  #Gibt alle Mitglieder aus, welche nacheinander erhöhen müssen


def biddingloop(message):
  global reaction
  global bidding_allowed
  global current_bidder
  global raise_reaction
  global raise_allowed
  global raise_player
  global High_Bidd_Error
  global NOT_INT_DATATYPE
  if bidding_allowed == True and message.author.name == round_members[current_bidder]:
    reaction = False
    if message.content.startswith("<check"):
      reaction = True   
      current_bidder +=1                     #end loop
    if message.content.startswith("<all_in"):
      global money_value
      money_value = money[round_members[current_bidder]]
      raise_reaction = True
      raise_player = global_raise(0)  
      raise_allowed = True 
      print("Raise_Player nach Methodenabruf:"+ str(raise_player))
      bidding_allowed = False
      round_money.update({str(round_members[current_bidder]):int(round_money[round_members[current_bidder]]) + int(money_value)})   #Einsatz des Spielers anpassen
      money.update({str(round_members[current_bidder]):0})
      round_members.remove(round_members[current_bidder])  #Spieler aus round_member entfernen, damit er nicht weiter gefragt wird, was er tun muss
      print("Potential Winners after all in: " + str(potential_winners))
      print("Round_Members after all in: " + str(round_members))
      current_bidder = 0
      print("Current_Bidder:" + str(current_bidder))  
      print("Round_money" + str(round_money))
      print("Executed ALL IN")
    if message.content.startswith("<raise"):
      #global money_value
      if  len(message.content.split(" ", 1)) == 2:
        money_value = message.content.split(" ", 1)[1]
        if int(money_value) < money[message.author.name]:
          raise_reaction = True
          raise_player = global_raise(1)  
          raise_allowed = True 
          print("Raise_Player nach Methodenabruf:"+ str(raise_player))
          bidding_allowed = False
          round_money.update({str(round_members[current_bidder]):int(round_money[round_members[current_bidder]]) + int(money_value)})
          money.update({str(round_members[current_bidder]):int(money[round_members[current_bidder]]) - int(money_value)})
          current_bidder = 0
        else:
          High_Bidd_Error = True
          print("Hide_Bidd_Error")
          print("Current_Bidder:" + str(current_bidder))  
        #else:
         # NOT_INT_DATATYPE = True
          #print("NOT_INT_DATATYPE")
          #print("Current_Bidder:" + str(current_bidder)) 
      else:
        money_value = 1
        if money_value < money[message.author.name]:
          raise_reaction = True 
          raise_player = global_raise(1) 
          raise_allowed = True     
          print("Raise_Player nach Methodenabruf:"+ str(raise_player))
          bidding_allowed = False  
          round_money.update({str(round_members[current_bidder]):int(round_money[round_members[current_bidder]]) + int(money_value)})
          money.update({str(round_members[current_bidder]):int(money[round_members[current_bidder]]) - int(money_value)})
          current_bidder = 0
        else:
          High_Bidd_Error = True
          print("Hide_Bidd_Error")
          print("Current_Bidder:" + str(current_bidder))  
      print("Current_Bidder:" + str(current_bidder))  
      print("Round_money" + str(round_money))
      print("Executed 1.Raise")
 
  # if raise_reaction == True and message.author.name == raise_player[current_bidder]: #Wenn jemand erhöht hat wird gefragt ob man mitgehen, rausgehen oder weiter erhöhen will
  #   raise_reaction = False  
  #   if message.content.startstwith("<call"):
  #     max_key = max(round_money.iteritems(), key=operator.itemgetter(1))[0]
  #     round_money.update({str(raise_player[current_bidder]):int(round_money[max_key])})
  #     raise_reaction = True
  #     print(round_money)

def raise_loop(message):
  global reaction
  global bidding_allowed
  global current_bidder
  global raise_allowed
  global raise_reaction
  global raise_player
  global High_Bidd_Error
  if raise_allowed == True and message.author.name == raise_player[current_bidder]: #Wenn jemand erhöht hat wird gefragt ob man mitgehen, rausgehen oder weiter erhöhen will
    raise_reaction = False  
    print(message.content)
    print(type(message.content))
    x = message.content
    if x.find('<call') != -1: #x.startstwith("<call"):      #mitgehen
      max_key = max(round_money.items(), key=operator.itemgetter(1))[0]
      money_value = int(round_money[max_key]) - int(round_money[raise_player[current_bidder]])
      round_money.update({str(raise_player[current_bidder]):int(round_money[max_key])})
      money.update({str(raise_player[current_bidder]):int(money[raise_player[current_bidder]]) - int(money_value)})
      raise_reaction = True
      print(round_money)
      current_bidder +=1
    if message.content.startswith("<fold"):
      global round_members
      global potential_winners
      print("Potential Winners before action: " + str(potential_winners))
      round_members.remove(raise_player[current_bidder])
      potential_winners.remove(raise_player[current_bidder])
      print("Round_Members: " + str(round_members))
      print("Potential Winners before remove: " + str(potential_winners))
      #potential_winners.remove(raise_player[current_bidder])
      print("Potential Winners after remove: " + str(potential_winners))
      print("Kicked out: " + str(raise_player[current_bidder]))                  #end loop
      raise_reaction = True
      current_bidder +=1

    if message.content.startswith("<all_in"):
      money_value = money[raise_player[current_bidder]]
      raise_allowed = True   
      raise_reaction = True
      print("Raise_Player nach Methodenabruf:"+ str(raise_player))
      max_key = max(round_money.items(), key=operator.itemgetter(1))[0]          #maximalwert und somit höchsten bieter herausfinden
      round_money.update({str(raise_player[current_bidder]):int(money_value) + int(round_money[raise_player[current_bidder]])})  #eigenen Einsatz auf den eigenen moneywert setzen
      money.update({str(raise_player[current_bidder]):0})
      remove_player = raise_player[current_bidder]
      raise_player = global_raise(1)  
      round_members.remove(str(remove_player))
      current_bidder = 0
      print("Raise_Player nach Methodenabruf:"+ str(raise_player))
      print("Potential Winners after all in: " + str(potential_winners))
      print("Round_Members after all in: " + str(round_members))
      bidding_allowed = False   
      print("Current_Bidder:" + str(current_bidder))  
      print("Round_money" + str(round_money))
      print("Executed 2.ALL IN")
   
    
    if message.content.startswith("<raise"):   #weiter erhöhen
      max_key = max(round_money.items(), key=operator.itemgetter(1))[0]
      if  len(message.content.split(" ", 1)) == 2:
        #global money_value
        money_value = message.content.split(" ", 1)[1]
        if (int(round_money[max_key]) - int(round_money[message.author.name])) + int(money_value)  < money[message.author.name]: #vergleicht ob der Spieler mehr geld als benötigt besitzt
          raise_allowed = True   
          raise_reaction = True
          print("Current_Bidder before changing round_money:" + str(current_bidder))
          max_key = max(round_money.items(), key=operator.itemgetter(1))[0]          #maximalwert und somit höchsten bieter herausfinden
          money_value = (int(round_money[max_key]) - int(round_money[raise_player[current_bidder]])) + int(money_value)
          #round_money.update({str(raise_player[current_bidder]):int(round_money[max_key])})  #eigenen Einsatz auf den des höchstbietenden setzen
          round_money.update({str(raise_player[current_bidder]):int(round_money[raise_player[current_bidder]]) + int(money_value)}) #Um den geannten Wert erhöhen 
          money.update({str(raise_player[current_bidder]):int(money[raise_player[current_bidder]]) - int(money_value)})
          current_bidder = 0
          raise_player = global_raise(1)  
          print("Raise_Player nach Methodenabruf:"+ str(raise_player))
          bidding_allowed = False   
        else:
          High_Bidd_Error = True
          print("Hide_Bidd_Error")
          print("Current_Bidder:" + str(current_bidder))  
      else:
        money_value = 1
        if (int(round_money[max_key]) - int(round_money[message.author.name])) + int(money_value)  < money[message.author.name]:
          raise_allowed = True 
          raise_reaction = True 
          print("Current_Bidder before changing round_money:" + str(current_bidder))
          max_key = max(round_money.items(), key=operator.itemgetter(1))[0]          #maximalwert und somit höchsten bieter herausfinden
          money_value = (int(round_money[max_key]) - int(round_money[raise_player[current_bidder]])) + int(money_value)
          #round_money.update({str(raise_player[current_bidder]):int(round_money[max_key])})  #eigenen Einsatz auf den des höchstbietenden setzen
          round_money.update({str(raise_player[current_bidder]):int(round_money[raise_player[current_bidder]]) + int(money_value)}) #Um den geannten Wert erhöhen 
          money.update({str(raise_player[current_bidder]):int(money[raise_player[current_bidder]]) - int(money_value)})
          current_bidder = 0
          raise_player = global_raise(1)    
          print("Raise_Player nach Methodenabruf:"+ str(raise_player))
          bidding_allowed = False  
        else:
          High_Bidd_Error = True
          print("Hide_Bidd_Error")
          print("Current_Bidder:" + str(current_bidder))  
      print("Current_Bidder:" + str(current_bidder))  
      print("Round_money" + str(round_money))
      print("Executed 2.Raise")
   
      
def auswertung():
  global hands
  global mid
  for player in hands:
    print(player)
  
  return






    

    



      




      
  

  



          # #Anfang Gebote
          # #-------------------------------------------------------
          # for x in round_members:
          #   channel = client.get_channel(pokertisch)
          #   await channel.send(str(x) + " choose between *<raise Value <check and  <fold*")
          #   reaction = False
          #   while reaction == False:
          #     print("Im in")
          #     print("Message: ", message)
          #     if message.author.name == x:
          #       if message.content.startswith("<check"):
          #         reaction = True                        #end loop
          #       if message.content.startswith("<fold"):
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































