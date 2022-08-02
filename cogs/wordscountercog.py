import discord
from botconfigs.config import BOT_RESTRICTIONS, BOT_PREFIX, DB_FILE
from botconfigs.database import Database
from discord.ext import commands


class WordsCounterCog(commands.Cog):

    def __init__(self, client):
        self.client = client


    def get_all_words(self):
        """ retrieve all words from database """

        with Database(DB_FILE) as db:
            return db.get_all_words()


    @commands.command()
    async def leaderboards(self, ctx, *args):
        """
            Display leaderboards for most users that mentions each monitored words.

            Params:
                ctx (message.context): message sent.
                (optional) *args (str list): monitored word to check
        """

        # only allow commands in bot-commands channel
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return

        # get all words from database
        monitored_words = self.get_all_words()

        # return if args is not recognized or has too many arguments
        if len(args) > 1 or len(args) == 1 and args[0] not in monitored_words[ctx.guild.id]:
            response = f'*Hey <@{ctx.author.id}>, I can\'t recognize the category.* Try a different one.'
            await ctx.send(response)
            return

        word = args[0] if args else None
        
        embed = None
        
        with Database(DB_FILE) as db:
            # leaderboards with specified word
            if word:
                leaderboards = db.get_leaderboards(guild_id=ctx.guild.id, word=word)
                print('  Showing leaderboards for {word}...')
                title=f'Top 5 Leaderboards for `{word.capitalize()}` ({ctx.guild.name})'
            # leaderboards
            else:
                leaderboards = db.get_leaderboards(guild_id=ctx.guild.id)
                print(f'  Showing leaderboards...')
                title=f'Top 5 Leaderboards ({ctx.guild.name})'
            
            embed = discord.Embed(
                title=title,
                color=0x5865f2)

            if len(leaderboards) == 1 and not list(leaderboards.values())[0]:
                embed.add_field(
                    name='Wow, such empty...',
                    value='It seems that no one has ever **mentioned** that word.\nMaybe you can be the first one! :wink:',
                )

            for word, results in leaderboards.items():
                # continue if no results for this word
                if not results:
                    continue

                value = ''
                for result in results:
                    member = await ctx.guild.fetch_member(
                        int(result['author']))
                    value += f'{member.name}#{member.discriminator} : `{result["count"]}`\n'

                embed.add_field(
                    name=word.capitalize(),
                    value=value,
                    inline=True)

        embed.add_field(
            name='\u1CBC\u1CBC',
            value=f'Type `{BOT_PREFIX}leaderboards` to display all leaderboards.' if args else f'Type `{BOT_PREFIX}leaderboards <monitored_word>` to display word-specific leaderboard.',
            inline=False
        )

        await ctx.send(content=None, embed=embed)
    

    @commands.group()
    async def monitored(self, ctx):

        # Only allow commands in bot-commands channel
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return

        if ctx.invoked_subcommand is None:
            response = f'Insufficient or invalid command. Try adding `words` at the end of the command.'
            await ctx.send(response)
    
    @monitored.command()
    async def words(self, ctx, *args):
        """
            Display all monitored words.

            Params:
                ctx (message.context): message sent.
        """

        # Only allow commands in bot-commands channel
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return

        # get all words from database
        monitored_words = self.get_all_words()

        # return if args is not recognized or has too many arguments
        if len(args) > 0:
            response = f'*Hey <@{ctx.author.id}>, I don\'t recognize the category.* Try a different one.'
            await ctx.send(response)
            return

        embed = discord.Embed(
            title='List of Monitored Words',
            color=0x5c64f4)

        with Database(DB_FILE) as db:

            # count total mentions of each monitored word
            print(f'  Calculating total mentions...')
            print(f'  Showing monitored words...')
            for word in monitored_words[ctx.guild.id]:
                total_mentions = db.count_mentions('word_counter',
                                                word=word)

                if total_mentions:
                    embed.add_field(
                        name=word.capitalize(),
                        value=f'Total mentions: `{total_mentions}`',
                        inline=True)

            embed.add_field(
                name='\u1CBC\u1CBC',
                value=f'Type `{BOT_PREFIX}leaderboards` to display all leaderboards.',
                inline=False)

        await ctx.send(content=None, embed=embed)


def setup(client):
    client.add_cog(WordsCounterCog(client))
    print('    WordsCounterCog loaded.')