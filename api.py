'''
	Bot for accessing osrs api

	user docs say that they want user agent set properly or they will block

	docs url: https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices#Latest_price_(all_items)
'''

import requests
from pathlib import Path
import argparse
from datetime import datetime, timedelta, timezone
import json
import time

class Geapi:

	def __init__(self):
		self.endpoint = "https://prices.runescape.wiki/api/v1/osrs"
		self.mappingCachePath = "./mapping.json"
		self.latestSnapshot = "./latest.json"
		self.itemMapping = None

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

	def saveAllItemsLatest(self):
		
		reqUrl = self.endpoint + "/latest"

		res = self.reqSession.get(reqUrl)

		res.raise_for_status()

		loadedJson = res.json()

		mappedResult = {
			"retrieved_at": int(time.time()),  # UTC unix seconds
			"items": loadedJson
		}

		with open(self.latestSnapshot, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)


	def saveMapping(self):
		reqUrl = self.endpoint + "/mapping"
		res = self.reqSession.get(reqUrl)
		res.raise_for_status()

		loadedJson = res.json()

		mappedResult = {
			"retrieved_at": int(time.time()),  # UTC unix seconds
			"items": loadedJson
		}

		with open(self.mappingCachePath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadMapping(self):
    	# Load existing cache
		with open(self.mappingCachePath, "r", encoding="utf-8") as f:
			self.itemMapping = json.load(f)

		TTL_SECONDS = 24 * 60 * 60
		retrieved_time = self.itemMapping["retrieved_at"]
		now = int(time.time())

		is_stale = (now - retrieved_time) >= TTL_SECONDS

		if is_stale:
			# Refresh once
			self.saveMapping()

			# Reload once
			with open(self.mappingCachePath, "r", encoding="utf-8") as f:
				self.itemMapping = json.load(f)   

	def searchMapping(self, itemId):
		itemId = int(itemId)
		for item in self.itemMapping["items"]:
			if item["id"] == itemId:
				return item
		return None
	
if __name__ == '__main__':

	geapi = Geapi()
	geapi.setup()
	geapi.loadMapping()
	geapi.saveAllItemsLatest()
	#print(geapi.searchMapping("892"))

	
