'''
	data script for accessing osrs api

	user docs say that they want user agent set properly or they will block

	docs url: https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices#Latest_price_(all_items)
'''

import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
import json
import time

class Geapi:

	def __init__(self):
		self.endpoint = "https://prices.runescape.wiki/api/v1/osrs"
		self.mappingCachePath = "./mapping.json"
		self.latestSnapshotPath = "./latest.json"
		self.fiveMinAveSnapshotPath = "./fiveMinAve.json"
		self.oneHourAveSnapshotPath = "./oneHourAve.json"
		self.sixHourAveSnapshotPath = "./sixHourAve.json"
		self.oneDayAveSnapshotPath = "./oneDayAve.json"
		self.itemMapping = None
		self.latestSnapshot = None
		self.fiveMinAveSnapshot = None
		self.oneHourAveSnapshot = None
		self.sixHourAveSnapshot = None
		self.oneDayAveSnapshot = None

		self.setup()
		# self.loadAllItemsLatest()
		# self.loadMapping()

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
		print("SENDING LATEST REQUEST")

		reqUrl = self.endpoint + "/latest"

		params = None

		if itemId:

			params = {"id": itemId}
		
			res = self.reqSession.get(reqUrl, params = params)

			return res

	def saveAllItemsLatest(self):
		print("SENDING LATEST ALL REQUEST")
		reqUrl = self.endpoint + "/latest"
		
		res = self.reqSession.get(reqUrl)
		res.raise_for_status()
	
		loadedJson = res.json()
		mappedResult = {
			"retrieved_at": int(time.time()),  # UTC unix seconds
			"data": loadedJson["data"]
		}

		with open(self.latestSnapshotPath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadAllItemsLatest(self):
		# Load existing cache
		with open(self.latestSnapshotPath, "r", encoding="utf-8") as f:
			self.latestSnapshot = json.load(f)

		TTL_SECONDS = 5 * 60
		retrieved_time = self.latestSnapshot["retrieved_at"]
		now = int(time.time())

		is_stale = (now - retrieved_time) >= TTL_SECONDS

		if is_stale:
			# Refresh once
			self.saveAllItemsLatest()

			# Reload once
			with open(self.latestSnapshotPath, "r", encoding="utf-8") as f:
				self.latestSnapshot = json.load(f) 

	def saveFiveMinAve(self):
		print("SENDING FIVE MIN AVE REQUEST")
		reqUrl = self.endpoint + "/5m"
		res = self.reqSession.get(reqUrl)
		res.raise_for_status()

		loadedJson = res.json()

		mappedResult = {
			"retrieved_at": int(time.time()), # UTC unix seconds
			"data": loadedJson["data"]
		}

		with open(self.fiveMinAveSnapshotPath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadFiveMinAve(self):

		# Load existing cache
		with open(self.fiveMinAveSnapshotPath, "r", encoding="utf-8") as f:
			self.fiveMinAveSnapshot = json.load(f)

		TTL_SECONDS = 5 * 60 # 5 minutes
		retrieved_time = self.itemMapping["retrieved_at"]
		now = int(time.time())

		is_stale = (now - retrieved_time) >= TTL_SECONDS

		if is_stale:
			# Refresh once
			self.saveFiveMinAve()

			# Reload once
			with open(self.fiveMinAveSnapshotPath, "r", encoding="utf-8") as f:
				self.fiveMinAveSnapshot = json.load(f)

	def saveMapping(self):
		print("SENDING MAPPING REQUEST")
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
	
	def getLatestSnapshot(self):
		#TODO: check if stale and if so get a new one
		return self.latestSnapshot
	
	def getItemMapping(self):
		#TODO: check if stale and if so get a new one
		return self.itemMapping
	
if __name__ == '__main__':

	geapi = Geapi()
	geapi.setup()
	geapi.saveFiveMinAve()
	# geapi.loadMapping()
	# geapi.loadAllItemsLatest()
	# print(geapi.searchMapping("892"))
	# print(geapi.searchLatestSnapshot("892"))

	
