import discord
import os
from YTDLSource import YTDLSource
from keep_alive import keep_alive
from Youtube import Youtube
from Video import Video
from Element import Element

from discord.ext import commands, tasks

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

async def show_search (videos, ctx):
  for video in videos:
    embed = discord.Embed(title=video.title, url=video.link,description=video.desc, color=0xFF5733) 
    embed.set_thumbnail(url=video.thumbnail)    

    embed.add_field(name='Views', value=video.views, inline=True)

    embed.add_field(name='Duration', value=video.duration, inline=True)

    embed.add_field(name='Comments', value=video.likes, inline=True)

    await ctx.send(embed=embed)
  
  await ctx.send(f'**✅  Choose a option (number) or cancel request with -1**')

@client.command()
async def commands (ctx):
  embed=discord.Embed(title="Commands", description="Here there all commands", color=0xFF5733)

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
async def yt (ctx, *args):
  global players
  global _queue
  
  search = " ".join(args[:])

  voice_state = ctx.author.voice

  if voice_state is None:
    await ctx.send('**❗ Join a channel**')
    return

  voice_channel = ctx.author.voice.channel

  if ctx.voice_client is None:
      await voice_channel.connect()
  
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

  await ctx.send(f'**🔎  Searching in Youtube: {search}**')

  videos = Youtube.get_videos(search, 4)

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
    player = await YTDLSource.from_url(url=videos[option - 1].link, loop = ctx.bot.loop, stream = True)
    players.append(player)
  except:
    del _queue[0]
    await ctx.send('**Error with this video**')
    return
  
  if voice.is_playing():
    await ctx.send('**✅  Inserted in queue**')
    return

  voice.play(player, after=lambda e: repeat(ctx.guild, voice, players))

  del players[0]

  await ctx.send(f'**🎶  Now Playing: {videos[option - 1].link}**')

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
      embed.add_field(name=element.video.title, value=element.video.desc, inline=True)

      embed.add_field(name='Duration', value=element.video.duration, inline=True)

      embed.add_field(name='Requester', value=element.requester, inline=True)

    await ctx.send(embed=embed)

keep_alive() 
client.run(os.getenv('TOKEN'))





