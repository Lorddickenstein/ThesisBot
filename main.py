import discord
import logging
import os
from botconfigs.config import *
from botconfigs.database import Database
from botconfigs.utils import get_local_time_now, get_datetime, format_date
from discord.ext import commands, tasks

token = os.getenv('BOT_TOKEN')
intents = discord.Intents.default()
client = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
# client.remove_command('help')     # HACK: native !help command from discord.py

# Discord Logs
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@client.event
async def on_ready():
    print('  Logged on as {0}!'.format(client.user))

    # TODO: Initialize global variables
    print('  Initializing global variables...')
    global EPICGAMES, DEVMODE

    print('    Initializing EPICGAMES...')
    EPICGAMES = client.get_cog('EpicGamesCog')

    # Turn DEVMODE off by default
    print('    Turning DEVMODE off by default...')
    DEVMODE = {0: False}

    print('  Global variables initialized...')

    if not check_epicgames_updates.is_running():
        check_epicgames_updates.start()

    print('  Bot ready, awaiting commands...')
    await client.change_presence(activity=discord.Game(name="!commands"))


@client.event
async def on_message(message):
    """
        Monitoring words without command invocations.

        params:
            message (message.context): message detected.
    """

    # ignore bot messages including self
    if message.author == client.user or message.author.bot:
        return

    # update MONITORED_WORDS
    print('    Initializing MONITORED_WORDS...')
    with Database(DB_FILE) as db:
        MONITORED_WORDS = db.get_all_words()
    
    print('Message from {0.author}: {0.content}'.format(message))

    msg = message.content.lower()
    guild_id = message.guild.id
    guild_name = message.guild.name
    author = message.author
    author_id = message.author.id

    # more like Bore Ragnarok! (callmekevin references - ignore this)
    if msg.endswith('more like'):
        response = 'Bore Ragnarok!'
        await message.channel.send(response)
    
    # apologetic people amirite? (thesis groupmates reference - also ignore this)
    if any(words in msg for words in SORRY_WORDS):
        response = 'Stop apologizing so much!!! It\'s **CRINGE!!!**'
        await message.channel.send(response)
    
    # word counter
    elif any(word in msg.split() for word in MONITORED_WORDS[guild_id]) and not msg.startswith(BOT_PREFIX):
        embed = discord.Embed(
            title='Word Counter (Server)',
            color=0x28b463)

        datetime_created = get_local_time_now('%Y-%m-%d %H:%M:%S')

        with Database(DB_FILE) as db:
            # insert all mentions of monitored words
            words_list = []
            for word in msg.split():
                if word in MONITORED_WORDS[guild_id]:
                    print(
                        f'  {word} has been mentioned by {author}.\n    Inserting {word} into database...')
                    db.insert_record('word_counter',
                                     author=author_id,
                                     word=word,
                                     datetime_created=format_date(datetime_created, '%Y-%m-%d %H:%M:%S'),
                                     guildId=guild_id)
                    words_list.append(word)
                    embed.add_field(
                        name=word.capitalize(),
                        value=f'Has been mentioned by <@{author_id}>',
                        inline=True)
            
            embed.add_field(
                name='\u1CBC\u1CBC',
                value='\u1CBC\u1CBC',
                inline=False)

            # count total mentions of monitored words
            words_list = dict.fromkeys(words_list)
            value = ''
            for word, _ in words_list.items():
                total_mentions = db.count_mentions('word_counter',
                                                   author=author_id,
                                                   word=word)
                value += f'**`{word.capitalize()}`** total mentions: `{total_mentions}`\n'
            
            embed.add_field(
                name=f'`{author}`\'s overall record in `{guild_name}`.',
                value=value,
                inline=False)

            embed.add_field(
                name='\u1CBC\u1CBC',
                value=f'Type `{BOT_PREFIX}leaderboards` to display leaderboards or `{BOT_PREFIX}monitored words` to display a list of monitored words.',
                inline=False)

        await message.channel.send(content=None, embed=embed)

    # Why does on_message make my commands stop working?
    # Overriding the default provided on_message forbids any extra commands from running.
    # To fix this, add a bot.process_commands(message) line at the end of your on_message.
    # For example:

    # @bot.event
    # async def on_message(message):
        # do some extra stuff here

        # await bot.process_commands(message)
    await client.process_commands(message)


@tasks.loop(seconds=1.0)
async def check_epicgames_updates():
    """ 
        Check if there are new updates in Epic Games Store every 24 hours
    """
    
    now  = get_local_time_now('%Y-%m-%d %H:%M:%S')

    # only check for updates at 11:00 PM Manila Time
    if now.time() != get_datetime('23:00:05', '%H:%M:%S').time():
        return

    with Database(DB_FILE) as db:
        # update games status before getting rows
        print('  Updating games in database...')
        db.update_game_status()
        games_db = db.get_games()

        # get current free games from epic games
        print('  Checking updates from Epic Games Store...')
        games = await EPICGAMES.get_updates()

        # insert new games into database
        ctr = 0
        for status, games_dict in games.items():
            for game in games_dict:
                if game not in games_db[status]:
                    ctr += 1 
                    db.insert_record('free_games',
                        title=game['title'],
                        gameId=game['gameId'],
                        description=game['description'],
                        startDate=format_date(game['startDate'], '%Y-%m-%d %H:%M:%S'),
                        endDate=format_date(game['endDate'], '%Y-%m-%d %H:%M:%S'),
                        url=game['url'],
                        icon=game['icon'],
                        status=game['status'])
        if ctr > 0:
            print('  Found {} new updates...'.format(ctr))

        # send embedded messages to discord channel #free-games-reminder
        print('  Showing current and upcoming free games...')
        for channel in client.get_all_channels():
            if (channel.type == discord.ChannelType.text) and (channel.name == 'free-games-reminder'):
                if ctr > 0:
                    await EPICGAMES.init()
                    await channel.send(f'Update as of **{format_date(now, "%b %d, %Y %I:%M %p")}**.\nEpic Games Store has updated their free games list. Check out the Epic Games Store now at https://store.epicgames.com/en-US/free-games/ to get your free games of the week.')
                    embeds = await EPICGAMES.get_embeds('now') + await EPICGAMES.get_embeds('later')
                    for embed in embeds:
                        await channel.send(content=None, embed=embed)
                # else:
                #     await channel.send(f'Update as of **{format_date(now, "%b %d, %Y %I:%M %p")}**. There are no new games today.')


@client.command()
async def commands(ctx):
    """
        List all commands.

        Params:
            ctx (message.context): message sent.
    """

    # only allow commands in bot-commands channel
    if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
        return

    embed = discord.Embed(
        title='Commands Lists',
        description='Hello, I\'m the product of your horrible thesis. Please refer to the commands below on how to use me.\n\u1CBC\u1CBC',
        color=0xf1c40f)

    print('  Showing commands list...')
    for command in BOT_COMMANDS:
        embed.add_field(
            name=BOT_PREFIX + command.get('command'),
            value=command.get('response'),
            inline=False)
    
    embed.set_footer(text='Bot created on July 8, 2022.')
    await ctx.send(content=None, embed=embed)
    

@client.command()
async def devmode(ctx, *args):
    """
        Toggle devmode.
        
        Params:
            ctx (message.context): message sent.
    """
    
    # Only allow commands in bot-commands channel
    if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
        return
    
    # return if args is not recognized or has too many arguments
    if len(args) > 1 or len(args) == 1 and args[0].lower() not in ['on', 'off']:
        response = f'Bruh it\'s `on` and `off` only. Try again.'
        await ctx.send(response)
        return

    global DEVMODE

    if ctx.guild.id not in DEVMODE:
        DEVMODE[ctx.guild.id] = False

    status = args[0] if len(args) == 1 else None

    if status == 'on':
        DEVMODE[ctx.guild.id] = True
        response = '`devmode` is now **on**.'
    elif status == 'off':
        DEVMODE[ctx.guild.id] = False
        response = '`devmode` is now **off**.'
    else:
        response = '`devmode` is currently **{}**.'.format('on' if DEVMODE[ctx.guild.id] else 'off')
    
    await ctx.send(response)


@client.command()
async def load(ctx, extension):
    """"
        Load an extension.
        
        Params:
            ctx (message.context): message sent.
            extension (str): extension to load.
    """

    # Only allow if devmode is on
    if not DEVMODE[ctx.guild.id]:
        await ctx.send(f'`devmode` is **off**.')
        return

    print(f'  Loading extension {extension}...')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'`{extension}` loaded.')


@client.command()
async def reload(ctx, extension):
    """
        Unload and loads an extension.
        Params:
            ctx (message.context): message sent.
            extension (str): extension to reload.
    """

    # Only allow if devmode is on
    if not DEVMODE[ctx.guild.id]:
        await ctx.send(f'`devmode` is **off**.')
        return
    
    print(f'  Reloading {extension}...')
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'`{extension}` reloaded.')


@client.command()
async def stats(ctx):
    """List bot information and statistics.
        Parameters:
            ctx (message.context): message sent.
    """

    # only allow commands in bot-commands channel
    if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
        return

    embed = discord.Embed(
        title='Thesis Bot Statistics',
        description='\u1CBC\u1CBC',
        url=f'https://discord.com/users/{client.user.id}',
        color=0x00aff4)

    embed.set_author(
        name='Thesis Bot',
        icon_url=client.user.avatar_url)

    # display bot statistics
    print('  Showing bot statistics...')
    for key, value in STATS.items():
        if key == 'Bot Developers':
            authors = []
            for val in value:
                member = await client.fetch_user(int(val['discordId']))
                authors.append(f'<@{val["discordId"]}> {member.name}#{member.discriminator}')
            value = '\n'.join(authors)
        
        embed.add_field(
            name=key,
            value=value)
    
    embed.set_footer(text=' ')

    await ctx.send(content=None, embed=embed)


@client.command()
async def test(ctx):
    """ development command for testing purposes """
    print(ctx.guild.id)


@client.command()
async def unload(ctx, extension):
    """
        Unload an extension. 

        Params:
            ctx (message.context): message sent.
            extension (str): extension to unload.
    """

    # Only allow if devmode is on
    if not DEVMODE[ctx.guild.id]:
        await ctx.send(f'`devmode` is **off**.')
        return

    print(f'  Unloading {extension}...')
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'`{extension}` unloaded.')


# Load all cogs
print('  Loading all cogs...')
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
print('  Getting bot ready...')

client.run(token)