# The Blue Bird - Discord Music Bot 🎵

A feature-rich Discord music bot built with `discord.py` and `yt-dlp` for seamless music playback, queue management, autoplay, and more.

 Category        | Details                                                                                   |
|-----------------|------------------------------------------------------------------------------------------|
| **Description** | Advanced music bot with queue management, autoplay, and YouTube integration              |
| **Core Tech**   | `discord.py`・`yt-dlp`・`FFmpeg`・`Python 3.8+`                                         |
| **Hosting**     | Requires 24/7 server・AWS/Replit/Raspberry Pi recommended                               |
| **Key Features**| Play/Pause/Skip・Volume Control・Autoplay・Queue System・Now Playing Display・Playlists |

## Features ✨
- **Play Music**: Play songs or playlists directly from YouTube.
- **Queue System**: Add multiple tracks to the queue and manage them.
- **Autoplay**: Automatically add related tracks from YouTube Mix or search when the queue ends.
- **Volume Control**: Adjust playback volume (0-100%).
- **Now Playing**: Display current song, duration, and progress.
- **24/7 Support**: Stay in voice channels indefinitely (hosting required).
- **Playback Controls**: Pause, resume, skip, and clear the queue.
- **Embed Messages**: Clean and visually appealing responses.

## Installation 📥

### Prerequisites
- Python 3.8 or higher
- FFmpeg (for audio processing)
- Discord Bot Token ([Get Started Here](https://discord.com/developers/applications))

### Steps
1. Clone this repository:
   ```bash
   git clone [https://github.com/Champ2979/Discord-Music-Bot.git]

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a .env file in the project root and add your Discord bot token:
    ```bash
    DISCORD_BOT_TOKEN=your_token_here
    ```
4. Run the bot.
    ```bash
    python Main_bot_Code.py
    ```
### Setup Bot Permissions 🔧
1. Enable Message Content, Server Members, and Voice States intents on the Discord Developer Portal.

2. Invite the bot to your server with the applications.commands scope and required permissions:

- View Channels.

- Send Messages.

- Connect and Speak (in voice channels).

### Commands List 🎹
| Command & Parameters           | Description                          | Aliases/Examples                     |
|---------------------------------|--------------------------------------|---------------------------------------|
| `+play <song/URL>`             | Play song or add to queue            | `+play https://youtu.be/...`          |
| `+skip`                        | Skip current track                   | -                                     |
| `+stop`                        | Pause playback                       | -                                     |
| `+resume`                      | Resume playback                      | -                                     |
| `+queue_list`                  | Show queued songs                    | -                                     |
| `+current`                     | Now playing info                     | `+np`, `+nowplaying`                  |
| `+volume <0-100>`              | Adjust volume                        | `+volume 75`                          |
| `+autoplay`                    | Toggle automatic queue continuation  | -                                     |
| `+clear`                       | Clear all queued tracks              | -                                     |
| `+join`                        | Join voice channel                   | -                                     |
| `+leave`                       | Disconnect from voice                | -                                     |
| `+commands_list`               | Show all commands                    | `+helpme`, `+commands`                |

### ⚙️ Configuration Requirements

| Component       | Details                                                                                  |
|-----------------|------------------------------------------------------------------------------------------|
| Discord Intents | `Message Content`・`Server Members`・`Voice States`                                      |
| Permissions     | `Connect`・`Speak`・`View Channels`・`Send Messages`                                    |
| Dependencies    | `PyNaCl` (voice encryption)・`python-dotenv` (environment variables)                    |

### 🚨 Troubleshooting

| Issue                        | Solution                                                                                 |
|------------------------------|-----------------------------------------------------------------------------------------|
| Bot won't join voice         | 1. Check voice permissions<br>2. Verify intents are enabled<br>3. Restart bot           |
| No audio playback            | 1. Confirm FFmpeg is installed<br>2. Check YouTube URL validity<br>3. Test volume level |
| Autoplay failures            | 1. Disable/re-enable autoplay<br>2. Check internet connection                           |
| Dependency errors            | Run `pip install --upgrade -r requirements.txt`                                        |

### 📌 Important Notes
- Required: FFmpeg installed and added to system PATH
- Recommended: Dedicated voice channel for bot usage
- Supported formats: YouTube videos/playlists, direct URLs
- Volume persists between tracks until changed

> **Warning**  
> Avoid playing age-restricted/content-blocked videos as they may cause playback failures