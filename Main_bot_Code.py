import discord
from discord.ext import commands, tasks
import yt_dlp as youtube_dl
import asyncio
from itertools import cycle
from collections import deque
from datetime import datetime
import discord.ext.commands
from dotenv import load_dotenv
import os
load_dotenv()

#Global variables
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
current_song_start = None
current_song_duration = None

current_volume = 0.5 
queue = deque()
current_song = None
autoplay_enabled = False
playback_offset = 0

bot = commands.Bot(command_prefix="+", intents=intents)
Status = cycle(['Hi there,this is the music bot The Blue Bird', 'Do Listening music for free', 'Have a great time here'])

# YouTube downloader options
ytdl_format_options = {
    'format': 'bestaudio/best[ext=webm]/bestaudio',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False, 
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    # 'format_sort': ['res:720', 'ext:mp3:m4a'],  # Prioritize MP3/M4A formats. Some issue occured regarding the format
    'socket_timeout': 30,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'hls'],
            'player_skip': ['configs'],
        }
    },
    'postprocessors': [{
        'key': 'SponsorBlock',
        'categories': ['music_offtopic']
    }]
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 128k -af "volume=0.5"',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

def create_embed(title, description, color=discord.Color.blue()):
    return discord.Embed(title=title, description=description, color=color)

@bot.event
async def on_ready():
    change_status.start()
    print("BOT IS ONLINE!!")

@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(Status)))

async def play_next(ctx):
    global current_song, autoplay_enabled, current_song_start, current_song_duration, current_volume, playback_offset
    
    if queue:
        current_song = queue.popleft()
        current_song_start = datetime.now()
        playback_offset = 0
        current_song_duration = current_song.get('duration')
        
        # Create audio source with volume control
        source = discord.FFmpegPCMAudio(current_song['url'], **ffmpeg_options)
        audio_source = discord.PCMVolumeTransformer(source, volume=current_volume)
        
        # Play the audio
        ctx.voice_client.play(
            audio_source,
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )
        
        # Send now playing embed
        embed = create_embed("Now Playing 🎶", f"[{current_song['title']}]({current_song['webpage_url']})")
        await ctx.send(embed=embed)
    
    # If queue is empty and autoplay is enabled
    else:
        if autoplay_enabled and current_song:
            try:
                # Attempt to fetch YouTube Mix
                mix_url = f"https://www.youtube.com/watch?v={current_song['id']}&list=RD{current_song['id']}"
                info = ytdl.extract_info(mix_url, download=False)
                
                # Verify playlist entries exist
                if not info.get('entries'):
                    raise Exception("No related tracks found in YouTube Mix")
                
                # Filter tracks: skip current song, shorts (<30s), and duplicates
                valid_tracks = [
                    t for t in info['entries'][1:]
                    if t.get('duration', 0) > 30 and t['id'] != current_song['id']
                ]
                
                if not valid_tracks:
                    raise Exception("No valid related tracks found")
                
                # Add up to 3 tracks to queue
                for track in valid_tracks[:3]:
                    queue.append(track)
                
                await ctx.send(embed=create_embed(
                    "Autoplay Added 🎧",
                    f"Added {len(valid_tracks[:3])} related tracks from YouTube Mix"
                ))
                await play_next(ctx)
                return
            
            except Exception as e:
                print(f"Autoplay Error: {str(e)}")
                # Fallback: search for similar music
                try:
                    search_query = f"music similar to {current_song['title']}"
                    search_info = ytdl.extract_info(f"ytsearch3:{search_query}", download=False)
                    if 'entries' in search_info:
                        valid_tracks = [
                            t for t in search_info['entries']
                            if t.get('duration', 0) > 30
                        ]
                        if valid_tracks:
                            for track in valid_tracks[:3]:
                                queue.append(track)
                            await ctx.send(embed=create_embed(
                                "Autoplay Added 🎧",
                                f"Added {len(valid_tracks[:3])} tracks from search"
                            ))
                            await play_next(ctx)
                            return
                        else:
                            raise Exception("No valid tracks in search results")
                    else:
                        raise Exception("Search returned no results")
                except Exception as search_e:
                    print(f"Search Error: {str(search_e)}")
                    await ctx.send("❌ Autoplay couldn’t find tracks to continue")
                    autoplay_enabled = False
        
        # If autoplay fails or is disabled, disconnect
        current_song = None
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Queue empty, leaving voice channel.")

# List of commands of the Bot
@bot.command(aliases=['commands', 'helpme'])
async def commands_list(ctx):
    """Sends a list of all available bot commands."""
    
    commands_info = {
        "+play <song/URL>": "Plays a song or adds it to the queue.",
        # "+pause": "Pauses the currently playing song.",
        "+resume": "Resumes the paused song.",
        "+skip": "Skips to the next song in the queue.",
        "+stop": "Playback paused. Use +resume to continue.",
        "+queue_list": "Shows the list of queued songs.",
        "+current / +np": "Displays the currently playing song.",
        "+clear": "Clears the song queue.",
        "+join": "Joins the voice channel.",
        "+leave": "Disconnects from the voice channel.",
        "+autoplay": "Toggles autoplay mode.",
        "+volume <0-100>": "Adjusts the volume.",
    }

    embed = discord.Embed(title="🎵 The Blue Bird - Commands List 🎵", 
                          description="Here are the commands you can use:", 
                          color=discord.Color.blue())

    for command, description in commands_info.items():
        embed.add_field(name=command, value=description, inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def volume(ctx, level: int):
    """Adjust volume (0-100)"""
    global current_volume  # Required to modify the global variable
    
    if not 0 <= level <= 100:
        return await ctx.send("❌ Volume must be between 0 and 100!")
    
    current_volume = level / 100  # Convert to 0.0-1.0 scale
    
    # Update volume for currently playing audio
    if ctx.voice_client and ctx.voice_client.is_playing():
        if isinstance(ctx.voice_client.source, discord.PCMVolumeTransformer):
            ctx.voice_client.source.volume = current_volume
    
    await ctx.send(f"🔊 Volume set to **{level}%**")
# 
# @bot.command()
# async def seek(ctx, time_str: str):

#     Seek to a specific time in the currently playing song.
#     Usage: +seek 30  (for 30 seconds) or !seek 1:30  (for 1 minute 30 seconds)
    
#     global playback_offset, current_song_start
    
#     # Check if a song is playing
#     if not current_song or not ctx.voice_client.is_playing():
#         return await ctx.send("No song is currently playing.")
    
#     # Check if the song has a duration (e.g., not a live stream)
#     if not current_song_duration:
#         return await ctx.send("Cannot seek in a live stream.")
    
#     # Parse the seek time
#     try:
#         seek_time = parse_time(time_str)
#     except ValueError as e:
#         return await ctx.send(str(e))
    
#     # Validate seek time
#     if seek_time < 0 or seek_time > current_song_duration:
#         return await ctx.send(f"Seek time must be between 0 and {current_song_duration} seconds.")
    
#     # Stop current playback
#     ctx.voice_client.stop()
    
#     # Create new FFmpeg options with seek time
#     before_options = f'-ss {seek_time} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
#     ffmpeg_options_seek = {
#         'before_options': before_options,
#         'options': '-vn -b:a 128k'
#     }
    
#     # Create new audio source
#     source = discord.FFmpegPCMAudio(current_song['url'], **ffmpeg_options_seek)
#     audio_source = discord.PCMVolumeTransformer(source, volume=current_volume)
    
#     # Update playback offset and start time
#     playback_offset = seek_time
#     current_song_start = datetime.now()
    
#     # Play the new source with the same after callback
#     ctx.voice_client.play(
#         audio_source,
#         after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
#     )
    
#     await ctx.send(f"⏩ Seeked to {seek_time // 60}:{seek_time % 60:02d}")

# """


@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command!")
        return
    await ctx.author.voice.channel.connect()
    await ctx.send("Connected to the voice channel!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not connected to any voice channel.")
@bot.command()
async def stop(ctx):
    """Pauses the current audio playback."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Playback paused. Use `+resume` to continue.")
    else:
        await ctx.send("❌ No audio is currently playing.")

@bot.command()
async def resume(ctx):
    """Resumes the paused audio playback."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Playback resumed.")
    else:
        await ctx.send("❌ No audio is currently paused.")

@bot.command()
async def play(ctx, *, search: str):
    # Ensure the bot is connected to a voice channel
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            await ctx.send(f"🔊 Joined {ctx.author.voice.channel} to play music!")
        else:
            await ctx.send("You need to be in a voice channel first. Use +join.")
            return

    try:
        # Extract information about the search query or playlist
        info = ytdl.extract_info(search, download=False)

        # Check if it's a playlist
        if 'entries' in info:
            # Add all tracks from the playlist to the queue
            for entry in info['entries']:
                if entry:  # Ensure the entry is not None
                    queue.append(entry)
                    await ctx.send(embed=create_embed("🎵 Added to Queue", f"[{entry['title']}]({entry['webpage_url']})"))
            
            # Notify the user about the playlist
            await ctx.send(embed=create_embed("🎶 Playlist Added", f"Added {len(info['entries'])} tracks from the playlist!"))
        
        # If it's a single video
        else:
            queue.append(info)
            await ctx.send(embed=create_embed("🎵 Added to Queue", f"[{info['title']}]({info['webpage_url']})"))

        # Start playing if not already playing or paused
        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await play_next(ctx)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def autoplay(ctx):
    global autoplay_enabled
    autoplay_enabled = not autoplay_enabled
    status = "enabled ✅" if autoplay_enabled else "disabled ❌"
    await ctx.send(embed=create_embed("Autoplay", f"Autoplay is now {status}"))

@bot.command()
async def queue_list(ctx):
    if queue:
        description = "\n".join([f"{idx+1}. [{song['title']}]({song['webpage_url']})" for idx, song in enumerate(queue)])
        await ctx.send(embed=create_embed("Current Queue 🎶", description))
    else:
        await ctx.send("The queue is currently empty.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipping to the next song!")
    else:
        await ctx.send("No song is currently playing.")

@bot.command()
async def clear(ctx):
    queue.clear()
    await ctx.send("🧹 The queue has been cleared!")

@bot.command(aliases=['np', 'nowplaying'])
async def current(ctx):
    if not current_song or not ctx.voice_client.is_playing():
        return await ctx.send("No song is currently playing")
    
    elapsed = datetime.now() - current_song_start
    elapsed_seconds = int(elapsed.total_seconds())
    
    # Format time display
    def format_time(seconds):
        if not seconds: return "Live"
        mins, secs = divmod(seconds, 60)
        return f"{mins}:{secs:02d}"
    
    duration_str = format_time(current_song_duration) if current_song_duration else "Live Stream"
    elapsed_str = format_time(elapsed_seconds)
    remaining_str = format_time(current_song_duration - elapsed_seconds) if current_song_duration else "--:--"
    
    embed = create_embed("Now Playing 🎵", 
                        f"[{current_song['title']}]({current_song['webpage_url']})")
    embed.add_field(name="Duration", value=f"{elapsed_str} / {duration_str}")
    embed.add_field(name="Remaining", value=remaining_str)
    
    await ctx.send(embed=embed)

    def parse_time(time_str):
    # """
    # Convert a time string to seconds.
    # Accepts integer seconds (e.g., "30") or MM:SS format (e.g., "1:30").
    # Raises ValueError on invalid input.
    # """
        try:
        # Try parsing as integer seconds
            return int(time_str)
        except ValueError:
        # Try parsing as MM:SS
            parts = time_str.split(':')
            if len(parts) == 2:
                try:
                    minutes = int(parts[0])
                    seconds = int(parts[1])
                    if seconds >= 60:
                        raise ValueError
                    return minutes * 60 + seconds
                except (ValueError, TypeError):
                    pass
            raise ValueError("Invalid time format. Use seconds (e.g., '30') or MM:SS (e.g., '1:30').")



# Run the bot using the token from the .env file
bot.run(os.getenv('DISCORD_BOT_TOKEN'))

