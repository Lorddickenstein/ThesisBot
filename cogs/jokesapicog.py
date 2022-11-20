import asyncio
import discord
from botconfigs.config import *
from discord.ext import commands
from dadjokes import Dadjoke
from jokeapi import Jokes


class JokesApiCog(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.command()
    async def dadjokes(self, ctx):
        """
            Make a ramdom dad joke.

            Params:
                ctx (message.context): message sent.
        """
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return
        
        dadjoke = Dadjoke()
        response = '*' + dadjoke.joke + '*'
        await ctx.send(response)


    @commands.command()
    async def jokes(self, ctx, *args):
        """
            Make a random joke. May take additional arg for the category of the joke.

            Read documentations for more info: https://github.com/leet-hakker/JokeAPI-Python

            params:
                ctx (message.context): message sent.
        """

        def find_specific_joke(jokes, category):
            for joke in jokes['jokes']:
                if joke['flags'][category]:
                    return joke
            return

        async def fetch_jokes():
            return await Jokes()

        # Only allow commands in bot-commands channel
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return

        # return if args is not recognized or has too many arguments
        if len(args) > 1 or len(args) == 1 and args[0] not in BLACKLISTED + CATEGORIES:
            response = f'*Hey <@{ctx.author.id}>, I can\'t recognize the category.* Try a different one.'
            await ctx.send(response)
            return
        
        category = args[0] if len(args) > 0 else None
        print('  Retrieving jokes from API...')
        try:
            j = await asyncio.wait_for(fetch_jokes(), timeout=5.0)
        except asyncio.TimeoutError:
            j = None

        # if server is down, return
        if j is None:
            response = f'*Hmmm, the server seems to be **down** at the moment. Please try again later.*'
            await ctx.send(response)
            return

        joke = None

        # jokes with category
        if category:
            print(f'  Searching for {category} joke...')
            if category in BLACKLISTED:
                while not joke:
                    jokes = await j.get_joke(amount=10)
                    joke = find_specific_joke(jokes, category)

            elif category in CATEGORIES:
                joke = await j.get_joke(category=[category])
        
        # jokes without category
        else:
            print(f'  Searching for any joke...')
            joke = await j.get_joke()
        
        if joke:
            print(f'  Joke found with category: {joke["category"]}, flags: {joke["flags"]}.')

            # one-liner jokes
            if joke['type'] == 'single':
                response = '*' + joke['joke'] + '*'
            
            # jokes with setup and delivery
            else:
                response = '*' + joke['setup'] + '*\n' + '*||' + joke['delivery'] + '||*'
            
            await ctx.send(response)
            print('  Joke delivered successfully.')


async def setup(client):
    await client.add_cog(JokesApiCog(client))
    print('    JokesApiCog loaded.')
