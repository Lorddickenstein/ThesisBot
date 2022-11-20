import discord
import json
from botconfigs.config import BOT_RESTRICTIONS, BOT_PREFIX
from botconfigs.utils import utc_to_local, get_local_time_now, get_uct_time, get_datetime, format_date
from discord.ext import commands
from requests_html import AsyncHTMLSession


class EpicGamesCog(commands.Cog):

    def __init__(self, client, locale='en-US', country='PH', session=None):
        self.session = AsyncHTMLSession() or session
        self.locale = locale
        self.country = country
        self.current_free_games = []
        self.next_free_games = []
        self.client = client


    def set_empty(self):
        """ empty the current and next free games lists"""

        self.current_free_games = []
        self.next_free_games = []
    
    
    async def get_embeds(self, period):
        games = self.current_free_games if period == 'now' else self.next_free_games
        embeds = []
        tag = '(Free Now)' if period == 'now' else '(Upcoming)'

        # no free games founds
        if not games:
            embed = discord.Embed(title='No games found...',
            description='Epic Games is currently not offering any free games.',
            color=0x484848)

            embed.set_author(
                name='Epic Games',
                url='https://store.epicgames.com/en-US/free-games/',
                icon_url='https://cdn2.unrealengine.com/Unreal+Engine%2Feg-logo-filled-1255x1272-0eb9d144a0f981d1cbaaa1eb957de7a3207b31bb.png')

            embed.add_field(
                name='\u1CBC\u1CBC',
                value='Disclaimer: This bot is not sponsored by Epic Games.',
                inline=False)

            embeds.append(embed)

            return embeds
        
        # free games found
        for game in games:
            embed = discord.Embed(
                title=f'{tag} {game["title"]}',
                description=game['description'],
                url=game['url'],
                color=0x484848)

            embed.set_author(
                name='Epic Games',
                url='https://store.epicgames.com/en-US/free-games/',
                icon_url='https://cdn2.unrealengine.com/Unreal+Engine%2Feg-logo-filled-1255x1272-0eb9d144a0f981d1cbaaa1eb957de7a3207b31bb.png')

            embed.set_thumbnail(url=game['icon'])
            embed.add_field(
                name='Promo Period: ',
                value=f'From **{format_date(game["startDate"], "%b %d, %Y %I:%M %p")}** to **{format_date(game["endDate"], "%b %d, %Y %I:%M %p")}**',
                inline=False)
            
            embed.add_field(
                name='Claim your free games now at the Epic Games Store!',
                value='Disclaimer: This bot is not sponsored by Epic Games.',
                inline=False)

            embeds.append(embed)

        return embeds
        

    async def fetch(self, allow_countries: str = None, verbose=False):
        if allow_countries is None:
            allow_countries = self.country

        url = f'''https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?=locale={self.locale}&country={self.country}&allowCountries={allow_countries}'''

        print(f'    Fetching data from url...') if verbose else None
        html = await self.session.get(url)
        if html:
            print(f'    Data received...') if verbose else None
            data = json.loads(html.text)
            return data

        print('    Data not recieved...') if verbose else None
        return
    

    async def init(self, verbose=False):
        # TODO: document this
        print('    Initializing games...') if verbose else None
        self.set_empty()
        result = await self.fetch(verbose)

        now = get_local_time_now()

        games = result['data']['Catalog']['searchStore']['elements']
        for game in games:
            img_src = ''
            for key_image in game['keyImages']:
                if key_image['type'] == 'OfferImageTall':
                    img_src = key_image['url']
                    break

            promotions = game['promotions']

            if promotions is None:
                continue

            current_promotions = promotions['promotionalOffers']
            upcoming_promotions = promotions['upcomingPromotionalOffers']
            if not current_promotions and not upcoming_promotions:
                continue

            slug = game['catalogNs']['mappings'][0]['pageSlug']
            url = f'https://store.epicgames.com/en-US/p/{slug}'

            # current promotions
            if current_promotions:
                current_promotions = current_promotions[0]['promotionalOffers']
                for promotion in current_promotions:

                    # get utc time
                    start_date = get_uct_time(promotion['startDate'][:-5])
                    end_date = get_uct_time(promotion['endDate'][:-5])

                    # convert to local time UTC/GMT+8 (Manila) and return datetime object
                    start_date = get_datetime(utc_to_local(start_date), '%Y-%m-%d %H:%M:%S')
                    end_date = get_datetime(utc_to_local(end_date), '%Y-%m-%d %H:%M:%S')

                    # ignore if expired
                    if end_date < now:
                        continue
                    
                    self.current_free_games.append({
                        'title': game['title'],
                        'gameId': game['id'],
                        'description': game['description'],
                        'startDate': start_date,
                        'endDate': end_date,
                        'url': url,
                        'icon':  img_src,
                        'status': 'active',
                    })

            # upcoming promotions
            if upcoming_promotions:
                upcoming_promotions = upcoming_promotions[0]['promotionalOffers']
                for promotion in upcoming_promotions:

                    # get utc time
                    start_date = get_uct_time(promotion['startDate'][:-5])
                    end_date = get_uct_time(promotion['endDate'][:-5])

                    # convert to local time UTC/GMT+8 (Manila) and return datetime object
                    start_date = get_datetime(utc_to_local(start_date), '%Y-%m-%d %H:%M:%S')
                    end_date = get_datetime(utc_to_local(end_date), '%Y-%m-%d %H:%M:%S')

                    self.next_free_games.append({
                        'title': game['title'],
                        'gameId': game['id'],
                        'description': game['description'],
                        'startDate': start_date,
                        'endDate': end_date,
                        'icon':  img_src,
                        'url': url,
                        'status': 'upcoming',
                    })

        print(f'    Found {len(self.current_free_games)} current free games...') if verbose else None
        print(f'    Found {len(self.next_free_games)} next free games...') if verbose else None


    async def get_updates(self, verbose=False):
        # TODO: document this
        await self.init(verbose)
        return {'active': self.current_free_games, 'upcoming': self.next_free_games}


    @commands.group()
    async def freegames(self, ctx):
        """
            Display free games. Invokes `.now` and `.later` subcommands.
            
            Params:
                ctx (message.context): message sent.
        """
        # Only allow commands in bot-commands channel
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return

        if ctx.invoked_subcommand is None:
            response = f'Insufficient or invalid command. Try adding `now` or `later` at the end of the command.'
            await ctx.send(response)


    @freegames.command()
    async def now(self, ctx):
        """
            Display current free games in Epic Game Store.

            params:
                ctx (message.context): message sent
        """

        # Only allow commands in bot-commands channel
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return

        await self.init(verbose=True)
        embeds = await self.get_embeds('now')
        for embed in embeds:
            await ctx.send(content=None, embed=embed)


    @freegames.command()
    async def later(self, ctx):
        """
            Display current free games in Epic Game Store.

            params:
                ctx (message.context): message sent
        """

        # Only allow commands in bot-commands channel
        if ctx.channel.name not in BOT_RESTRICTIONS['allowed-channels']:
            return

        await self.init(verbose=True)
        embeds = await self.get_embeds('later')
        for embed in embeds:
            await ctx.send(content=None, embed=embed)
        

async def setup(client):
    await client.add_cog(EpicGamesCog(client))
    print('    EpicGamesCog extension loaded.')
