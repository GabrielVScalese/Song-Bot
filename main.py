import discord
import os
from YTDLSource import YTDLSource
from keep_alive import keep_alive
from Youtube import Youtube
from Element import Element

from discord.ext import commands

client = commands.Bot(command_prefix='!a')

players = []
_queue = []

def repeat(guild, voice, players):
  if len(players) == 0:
      del _queue[0]
      return

  del _queue[0]

  voice.play(players.pop(0), after=lambda e: repeat(guild, voice, players))
  voice.is_playing()

async def show_new_element (ctx):
    await ctx.send(f'**✅  Inserted in queue:**')

    embed = discord.Embed(color=0xFF5733)

    embed.set_thumbnail(url=_queue[len(_queue) - 1].video.thumbnail)    

    embed.add_field(name=_queue[len(_queue) - 1].video.title, value=_queue[len(_queue) - 1].video.link, inline=True)

    embed.add_field(name='Duration', value=_queue[len(_queue) - 1].video.duration, inline=False)

    embed.add_field(name='Position', value=str(len(_queue)), inline=False)

    embed.add_field(name='Requester', value=_queue[len(_queue) - 1].requester, inline=False)

    await ctx.send(embed=embed)

async def show_search (videos, ctx):
  for video in videos:
    embed = discord.Embed(title=video.title, url=video.link,description=video.desc, color=0xFF5733) 
    embed.set_thumbnail(url=video.thumbnail)    

    embed.add_field(name='Views', value=video.views, inline=True)

    embed.add_field(name='Duration', value=video.duration, inline=True)

    embed.add_field(name='Comments', value=video.likes, inline=True)

    await ctx.send(embed=embed)
  
  await ctx.send(f'**🎵  Choose a option (number) or cancel request with -1**')

@client.event
async def on_ready():
  await client.change_presence(activity=discord.activity.Game('!acommands'))
  print('Bot is ready!')

@client.command()
async def commands (ctx):
  embed=discord.Embed(title="Commands", description="Here there are all commands", color=0xFF5733)

  embed.set_author(name=client.user.name, icon_url='https://i.ytimg.com/vi/esX7SFtEjHg/maxresdefault_live.jpg')

  embed.add_field(name="!acommands", value="The bot shows all commands", inline=False)

  embed.add_field(name="!ayt", value="The bot plays a youtube video", inline=False)

  embed.add_field(name="!askip", value="The bot skips the current video", inline=False)

  embed.add_field(name="!astop", value="The bot pauses the current video", inline=False)

  embed.add_field(name="!aresume", value="The bot resumes the current video", inline=False)

  embed.add_field(name="!aleave",value="The bot leaves the channel", inline=False)

  embed.set_footer(text='by gabriel s', icon_url='https://pbs.twimg.com/profile_images/1316750214/evandro_400x400.jpg') 
  
  await ctx.send(embed=embed)

@client.command()
async def yt (ctx, num, *args):
  global players
  global _queue
  
  try:
    search_num = int (num)
  except:
    await ctx.send('**❗ Invalid number of search, canceled request**')
    return

  search = " ".join(args[:])

  voice_state = ctx.author.voice

  if voice_state is None:
    await ctx.send('**❗  Join a channel**')
    return

  voice_channel = ctx.author.voice.channel

  channel_name = str(voice_channel)

  if ctx.voice_client is None:
      await voice_channel.connect()
      await ctx.send(f'**✅  Joined in {channel_name}**')
  
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  await ctx.send(f'**🔎  Searching {search_num} videos in Youtube: {search}**')

  videos = Youtube.get_videos(search, search_num)

  if len(videos) > 0:
    await ctx.send(f'**🆗  Found {len(videos)} results**')
  else:
    await ctx.send('**❗  Unfortunately the request limit has expired**')
    return

  await show_search(videos, ctx)

  msg = await client.wait_for("message", check=lambda message: message.author == ctx.author)

  try:
    option = int(msg.content)
  except:
    await ctx.send('**❗  Request canceled, invalid option**')
    return

  if option == -1:
     await ctx.send('**❗  Request canceled**')
     return
  elif option > len(videos):
    await ctx.send('**❗  Request canceled, invalid option**')
    return

  _queue.append(Element(msg.author, videos[option - 1]))

  try:
    player = await YTDLSource.from_url(url=videos[option - 1].link, stream = True)
    players.append(player)
  except:
    del _queue[len(_queue) - 1]
    await ctx.send('**❗  Error with this video, canceled request**')
    return
  
  if voice.is_playing():
    await show_new_element(ctx)
    return

  voice.play(player, after=lambda e: repeat(ctx.guild, voice, players))

  del players[0]

  await ctx.send(f'**🎶  Now playing: {videos[option - 1].link}**')

@client.command()
async def skip (ctx):
  global players
  global _queue

  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  if not voice.is_playing() or len(players) == 0:
    await ctx.send('**❗  Skip is not possible**')
    return
  
  del _queue[0]

  voice.pause()
  voice.play(players.pop(0), after=lambda e: repeat(ctx.guild, voice, players))

  await ctx.send('**⏭️  Song skipped**')

@client.command()
async def stop (ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  if not voice.is_playing():
    await ctx.send('**❗  Stop is not possible**')
    return
  
  voice.pause()

  await ctx.send('**⏹️  The song is paused**')

@client.command()
async def resume (ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  if not voice:
    await ctx.send('**❗ Resume is not possible**')
    return
  
  voice.resume()

  await ctx.send('**▶️  The song returned**')

@client.command()
async def leave (ctx):
  global players
  global _queue

  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  if voice:
    voice.pause()

  if (ctx.voice_client):
    await ctx.guild.voice_client.disconnect()
    await ctx.send('**❗  Disconnected**')
    players = []
    _queue = []
  else:
    await ctx.send("**❗  Already disconnected**")

@client.command()
async def queue (ctx):
  if len(_queue) == 0:
    await ctx.send('**❗  The queue is empty**')
  else:
    embed = discord.Embed(title='Queue',description='All the videos in queue', color=0xFF5733)

    for element in _queue:
      embed.add_field(name=element.video.title, value=element.video.link, inline=True)

      embed.add_field(name='Duration', value=element.video.duration, inline=True)

      embed.add_field(name='Requester', value=element.requester, inline=True)

    await ctx.send(embed=embed)

@client.command()
async def now (ctx):
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  if not voice:
    await ctx.send('**❗ Nothing is playing**')
    return
  
  await ctx.send('**🎶  Now is playing: **')

  embed = discord.Embed(color=0xFF5733)

  embed.set_thumbnail(url=_queue[0].video.thumbnail)    

  embed.add_field(name=_queue[0].video.title, value=_queue[0].video.link, inline=True)

  embed.add_field(name='Duration', value=_queue[0].video.duration, inline=False)

  embed.add_field(name='Requester', value=_queue[0].requester, inline=False)

  await ctx.send(embed=embed)


keep_alive() 
client.run(os.getenv('TOKEN'))





