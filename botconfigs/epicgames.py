import json
from datetime import datetime
from pathlib import Path
from requests_html import HTMLSession
from .config import BASE_DIR

class EpicGames:

	def __init__(self, locale='en-US', country='PH', session=None):
		self.session = HTMLSession() or session
		self.locale = locale
		self.country = country
		self.current_free_games = []
		self.next_free_games = []

	def fetch(self, allow_countries: str = None):
		if allow_countries is None:
			allow_countries = self.country

		url = f'''https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?=locale={self.locale}&country={self.country}&allowCountries={allow_countries}'''

		print(f'    Fetching data from {url}...')
		html = self.session.get(url)
		if html:
			print(f'    Data received...')
			data = json.loads(html.text)
			return data

		print('    Data not recieved...')
		return


	def init(self):
		print('    Initializing games...')
		result = self.fetch()

		now = datetime.now()
		date_now = datetime.strptime(now.strftime('%Y-%m-%d'), '%Y-%m-%d')
		time_now = datetime.strptime(now.strftime('%H:%M:%S'), '%H:%M:%S')

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
					startDate = datetime.fromisoformat(promotion['startDate'][:-1] + '+00:00')
					start_date = datetime.strptime(startDate.strftime('%Y-%m-%d'), '%Y-%m-%d')

					endDate = datetime.fromisoformat(promotion['endDate'][:-1] + '+00:00')
					end_date = {
						'endDate': datetime.strptime(endDate.strftime('%Y-%m-%d'), '%Y-%m-%d'),
						'time': datetime.strptime(endDate.strftime('%H:%M:%S'), '%H:%M:%S'),
					}

					start_date = {
						'startDate': start_date,
					}

					# ignore if expired
					if end_date['endDate'] < date_now:
						continue

					if end_date['endDate'] == date_now:
						if end_date['time'] < time_now or abs((end_date['endDate'] - start_date['startDate']).days) > 7:
							continue
		            
					self.current_free_games.append({
						'title': game['title'],
						'description': game['description'],
						'src':  img_src,
						'startDate': startDate.strftime('%m-%d-%Y %I:%M %p'),
						'endDate': endDate.strftime('%m-%d-%Y %I:%M %p'),
						'url': url,
					})

			# upcoming promotions
			if upcoming_promotions:
				upcoming_promotions = upcoming_promotions[0]['promotionalOffers']
				for promotion in upcoming_promotions:
					startDate = datetime.fromisoformat(promotion['startDate'][:-1] + '+00:00')
					endDate = datetime.fromisoformat(promotion['endDate'][:-1] + '+00:00')
					self.next_free_games.append({
						'title': game['title'],
						'description': game['description'],
						'src':  img_src,
						'startDate': startDate.strftime('%m-%d-%Y %I:%M %p'),
						'endDate': endDate.strftime('%m-%d-%Y %I:%M %p'),
						'url': url,
					})
		print('    Games initialized...')
		print(f'    Found {len(self.current_free_games)} current free games...')
		print(f'    Found {len(self.next_free_games)} next free games...')

	def get_current_free_games(self):
		return self.current_free_games

	def get_next_free_games(self):
		return self.next_free_games


if __name__ == '__main__':
	api = EpicGames()
	api.init()

	current_games = api.get_current_free_games()
	for game in current_games:
		print('Title:', game['title'])
		print('description:', game['description'])
		print('src:', game['src'])
		print('startDate', game['startDate'])
		print('endDate', game['endDate'])
		print('url', game['url'])

	print()
	next_games = api.get_next_free_games()
	for game in next_games:
		print('Title:', game['title'])
		print('description:', game['description'])
		print('src:', game['src'])
		print('startDate', game['startDate'])
		print('endDate', game['endDate'])
		print('url', game['url'])
