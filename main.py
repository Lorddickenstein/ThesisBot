import discord
import logging
import os
from botconfigs.config import *
from botconfigs.database import Database
from dadjokes import Dadjoke
from datetime import datetime
from discord.ext import commands
from jokeapi import Jokes

token = os.getenv('BOT_TOKEN')
prefix = '!'
intents = discord.Intents.default()
client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command('help')

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
    print('Logged on as {0}!'.format(client.user))

    print('  Initializing global variables...')
    global WORDS_COUNTED
    with Database(DB_FILE) as db:
        WORDS_COUNTED = db.get_all_words()

    await client.change_presence(activity=discord.Game(name="your mom"))


@client.event
async def on_message(message):
    """Monitoring words without command invocation.
        Parameters:
            message (message.context): message detected.
    """
    print('Message from {0.author}: {0.content}'.format(message))

    # ignore bot messages including self
    if message.author == client.user or message.author.bot:
        return

    msg = message.content.lower()
    author = message.author
    author_id = message.author.id

    # more like Bore Ragnarok! (callmekevin references - ignore this)
    if msg.endswith('more like'):
        response = 'Bore Ragnarok!'
        await message.channel.send(response)

    # apologetic people amirite? (thesis groupmates reference - also ignore this)
    elif any(words in msg for words in SORRY_WORDS):
        response = 'Stop apologizing so much!!! It\'s **CRINGE!!!**'
        await message.channel.send(response)

    # word counter
    elif any(word in msg.split() for word in WORDS_COUNTED) and not msg.startswith(prefix):
        embed = discord.Embed(
            title='Word Counter (Global)',
            color=0x28b463)
        date_now = datetime.now()
        datetime_created = date_now.strftime('%Y-%m-%d %H:%M')

        with Database(DB_FILE) as db:
            # insert all mentions of monitored words
            words_list = []
            for word in msg.split():
                if word in WORDS_COUNTED:
                    print(
                        f'  {word} has been mentioned by {author}. Inserting to database...')
                    db.insert_record('word_counter',
                                     author=author_id,
                                     word=word,
                                     datetime_created=datetime_created)
                    words_list.append(word)
                    embed.add_field(
                        name=word.capitalize(),
                        value=f'Has been mentioned by <@{author_id}>',
                        inline=False)

            # count total mentions of monitored words
            words_list = dict.fromkeys(words_list)
            print(
                f'  Calculating total mentions of monitored words by {author}')
            for word, _ in words_list.items():
                total_mentions = db.count_mentions('word_counter',
                                                   author=author_id,
                                                   word=word)
                embed.add_field(
                    name=word.capitalize(),
                    value=f'Total mentions: `{total_mentions}`',
                    inline=False)

            embed.add_field(
                name='\u1CBC\u1CBC',
                value=f'Type `{prefix}leaderboards` to display leaderboards or `{prefix}monitored words` to display a list of monitored words.',
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

# Test / Template Command


@client.command()
async def test(ctx, *, arg):
    if arg == 'help':
        print('ahh')
    else:
        print(arg)
    # WORDS_COUNTED.append(arg)
    # print(WORDS_COUNTED)
    await ctx.send('hello')


@client.command()
async def commands(ctx):
    """Lists commands available.
        Parameters:
            ctx (message.context): message sent.
    """
    embed = discord.Embed(
        title='Commands Lists',
        description='Hello, I\'m the product of your horrible thesis. Please refer to the commands below on how to use me.\n\u1CBC\u1CBC',
        color=0xf1c40f)

    print('  Showing commands list...')
    for command in COMMANDS:
        embed.add_field(
            name=prefix + command.get('command'),
            value=command.get('response'),
            inline=True)

    embed.set_footer(text='Bot created on July 8, 2022.')
    await ctx.send(content=None, embed=embed)


@client.command()
async def dadjokes(ctx):
    """Show a dad joke.
        Parameters:
            ctx (message.context): message sent.
    """
    dadjoke = Dadjoke()
    response = '*' + dadjoke.joke + '*'
    await ctx.send(response)


@client.command()
async def jokes(ctx, *args):
    """Output a joke. Can have optional args for the category of jokes.
        Parameters:
            ctx (message.context): message sent.
            args (str): joke category.
    """
    def find_specific_joke(jokes, category):
        for joke in jokes['jokes']:
            if joke['flags'][category]:
                return joke
        return

    # Invalid input
    if len(args) > 1:
        response = f'Sorry, your command is invalid. Try `{prefix}commands` for a complete list of valid commands.'
        await ctx.send(response)
        return

    category = args[0] if args else None

    print('  Retrieving jokes...')
    j = await Jokes()
    joke = None

    # jokes with category
    if category:
        print(f'  Searching for {category} jokes...')
        if category in BLACKLISTED:
            jokes = await j.get_joke(amount=10)
            while True:
                joke = find_specific_joke(jokes, category)
                if joke:
                    break
        elif category in CATEGORIES:
            joke = await j.get_joke(category=[category])
        else:
            print(f'  No such joke with {category} category...')
            response = f'Sorry, there is no such category for `{category}` jokes in my database.'
            await ctx.send(response)

    # jokes without categories
    else:
        joke = await j.get_joke()

    if joke:
        print(
            f'  Joke found with category: {joke["category"]}, flags: {joke["flags"]}...')

        # one-liner jokes
        if joke['type'] == 'single':
            response = joke['joke']
            await ctx.send(response)

        # jokes with setup and delivery
        else:
            response = '*' + joke['setup'] + '*'
            await ctx.send(response)
            response = '*||' + joke['delivery'] + '||*'
            await ctx.send(response)

        print('  Joke delivered successfully...')


@client.command()
async def leaderboards(ctx, *args):
    """Display leaderboards of monitored words.
        Parameters:
            ctx (message.context): message sent.
            *args (str): monitored word to check.
    """
    word = args[0] if args else None

    # Invalid input
    if len(args) > 1:
        print(f'  Invalid commands for {prefix}leaderboards {args}...')
        response = f'Sorry, your command is invalid. Try `{prefix}commands` for a complete list of valid commands.'
        await ctx.send(response)
        return
    elif word and word not in WORDS_COUNTED:
        print(f'  Invalid commands for {prefix}leaderboards {args}...')
        response = f'The word `{word}` is currently not being monitored. Use `{prefix}monitored_words` to display a list of monitored words.'
        await ctx.send(response)
        return

    embed = discord.Embed(
        title='Leaderboards',
        color=0x5865f2)

    with Database(DB_FILE) as db:
        # leaderboards with specified word
        if word:
            leaderboards = db.get_leaderboards(word=word)
            print('  Showing leaderboards for {word}...')
        # leaderboards
        else:
            leaderboards = db.get_leaderboards()
            print(f'  Showing leaderboards...')
        for word, results in leaderboards.items():
            value = ''
            for result in results:
                member = await ctx.guild.fetch_member(
                    int(result['author']))
                value += f'{member.name}#{member.discriminator} : `{result["count"]}`\n'

            embed.add_field(
                name=word.capitalize(),
                value=value,
                inline=True)

    value = f'Type `{prefix}leaderboards` to display all leaderboards.' if args else f'Type `{prefix}leaderboards <monitored_word>` to display word-specific leaderboard.'
    embed.add_field(
        name='\u1CBC\u1CBC',
        value=value,
        inline=False)
    await ctx.send(content=None, embed=embed)


# TODO: This cmd is lame af
@client.group()
async def monitored(ctx):
    if ctx.invoked_subcommand is None:
        response = f'Sorry, your command is insufficient. Try `{prefix}commands` for a complete list of valid commands.'
        await ctx.send('response')


@monitored.command()
async def words(ctx):
    """Display monitored words.
        Parameters:
            ctx (message.context): message sent.
    """
    embed = discord.Embed(
        title='List of Monitored Words',
        color=0x5c64f4)

    with Database(DB_FILE) as db:
        print(f'  Calculating total mentions...')
        print(f'  Showing monitored words...')
        # count total mentions of each monitored word
        for word in WORDS_COUNTED:
            total_mentions = db.count_mentions('word_counter',
                                               word=word)
            embed.add_field(
                name=word.capitalize(),
                value=f'Total mentions: `{total_mentions}`',
                inline=True)
        embed.add_field(
            name='\u1CBC\u1CBC',
            value=f'Type `{prefix}leaderboards` to display all leaderboards.',
            inline=False)
    await ctx.send(content=None, embed=embed)


@client.command()
async def stats(ctx):
    """List bot information and statistics.
        Parameters:
            ctx (message.context): message sent.
    """
    embed = discord.Embed(
        title='Thesis Bot Statistics',
        description='\u1CBC\u1CBC',
        url=f'https://discord.com/users/{ctx.author.id}',
        color=0x00aff4)
    embed.set_author(
        name='Thesis Bot',
        icon_url=client.user.avatar_url)

    print('  Showing bot statistics...')
    for key, value in STATS.items():
        embed.add_field(
            name=key,
            value=value)
    await ctx.send(content=None, embed=embed)


client.run(token)
