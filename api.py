'''
	Bot for accessing osrs api

	user docs say that they want user agent set properly or they will block

	docs url: https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices#Latest_price_(all_items)
'''

import requests
from pathlib import Path

class Geapi:

	def __init__(self):
	  self.endpoint = "https://prices.runescape.wiki/api/v1/osrs"
	  self.mappingCachePath = "./mapping.json"

	# sets up things like session and the user agent
	def setup(self):
		self.reqSession = requests.Session()

		# set up User Agent
		self.reqSession.headers.update(
			{
				"User-Agent": "OSRS GE Market Making/Price arbitrage script - Email: boyd.jc.github@gmail.com",
				"From": "boyd.jc.github@gmail.com"
			}
		)

	def latest(self, itemId=None):

		reqUrl = self.endpoint + "/latest"

		params = None

		if itemId:

			params = {"id": itemId}
		
			res = self.reqSession.get(reqUrl, params = params)

			print(res.text)

	def mapping(self):

		reqUrl = self.endpoint + "/mapping"

		res = self.reqSession.get(reqUrl)

		print(res.json)
	

if __name__ == '__main__':

	geapi = Geapi()
	geapi.setup()
	geapi.mapping()

	
