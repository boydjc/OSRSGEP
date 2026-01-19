'''
	Bot for accessing osrs api

	user docs say that they want user agent set properly or they will block

	docs url: https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices#Latest_price_(all_items)
'''

import requests

class Geapi:

	def __init__(self):
	  print("Hello from Geapi")
	  self.endpoint = "prices.runescape.wiki/api/v1/osrs"
	  print("Endpoint: ", self.endpoint)
	  self.testItemId = "892" # rune arrow

	# sets up things like user agent
	# docs say that they want a user agent or they will block requests
	def setup(self):
		pass
	

if __name__ == '__main__':

	geapi = Geapi()

	
