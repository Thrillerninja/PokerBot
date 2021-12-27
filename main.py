import discord

class MyClient(discord.Client):
  async def on_ready(self):
    print("Online")

  @client.event
  async def on_message(message):
    
client = MyClient()
client.run("OTI0OTg4MjQ3MTQ1MzQ5MTgw.Ycmkbw.q_Kdtk9MsJgVZ_Qu8on-ZPUrfsY")
