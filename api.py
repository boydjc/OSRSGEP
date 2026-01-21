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
		self.mappingCachePath = "./data/mapping.json"
		self.latestSnapshotPath = "./data/latest.json"
		self.fiveMinAveSnapshotPath = "./data/fiveMinAve.json"
		self.oneHourAveSnapshotPath = "./data/oneHourAve.json"
		self.sixHourAveSnapshotPath = "./data/sixHourAve.json"
		self.oneDayAveSnapshotPath = "./data/oneDayAve.json"
		self.itemMapping = None
		self.latestSnapshot = None
		self.fiveMinAveSnapshot = None
		self.oneHourAveSnapshot = None
		self.sixHourAveSnapshot = None
		self.oneDayAveSnapshot = None

		self.setup()

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

		Path(self.latestSnapshotPath).parent.mkdir(parents=True, exist_ok=True)

		with open(self.latestSnapshotPath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadAllItemsLatest(self):

		if Path(self.latestSnapshotPath).exists():

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
		else:
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

		Path(self.fiveMinAveSnapshotPath).parent.mkdir(parents=True, exist_ok=True)

		with open(self.fiveMinAveSnapshotPath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadFiveMinAve(self):

		if Path(self.fiveMinAveSnapshotPath).exists():

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
		else:
			self.saveFiveMinAve()

			# Reload once
			with open(self.fiveMinAveSnapshotPath, "r", encoding="utf-8") as f:
				self.fiveMinAveSnapshot = json.load(f)

	def saveOneHourAve(self):
		print("SENDING ONE HOUR AVE REQUEST")
		reqUrl = self.endpoint + "/1h"
		res = self.reqSession.get(reqUrl)
		res.raise_for_status()

		loadedJson = res.json()

		mappedResult = {
			"retrieved_at": int(time.time()), # UTC unix seconds
			"data": loadedJson["data"]
		}

		Path(self.oneHourAveSnapshotPath).parent.mkdir(parents=True, exist_ok=True)

		with open(self.oneHourAveSnapshotPath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadOneHourAve(self):

		if Path(self.oneHourAveSnapshotPath).exists():

			# Load existing cache
			with open(self.oneHourAveSnapshotPath, "r", encoding="utf-8") as f:
				self.oneHourAveSnapshot = json.load(f)

			TTL_SECONDS = 60 * 60 # 1 hour 
			retrieved_time = self.itemMapping["retrieved_at"]
			now = int(time.time())

			is_stale = (now - retrieved_time) >= TTL_SECONDS

			if is_stale:
				# Refresh once
				self.saveOneHourAve()

				# Reload once
				with open(self.oneHourAveSnapshotPath, "r", encoding="utf-8") as f:
					self.oneHourAveSnapshot = json.load(f)
		else:
			self.saveOneHourAve()

			# Reload once
			with open(self.oneHourAveSnapshotPath, "r", encoding="utf-8") as f:
				self.oneHourAveSnapshot = json.load(f)

	def saveSixHourAve(self):
		print("SENDING SIX HOUR AVE REQUEST")
		reqUrl = self.endpoint + "/6h"
		res = self.reqSession.get(reqUrl)
		res.raise_for_status()

		loadedJson = res.json()

		mappedResult = {
			"retrieved_at": int(time.time()), # UTC unix seconds
			"data": loadedJson["data"]
		}

		Path(self.sixHourAveSnapshotPath).parent.mkdir(parents=True, exist_ok=True)

		with open(self.sixHourAveSnapshotPath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadSixHourAve(self):

		if Path(self.sixHourAveSnapshotPath).exists():

			# Load existing cache
			with open(self.sixHourAveSnapshotPath, "r", encoding="utf-8") as f:
				self.sixHourAveSnapshot = json.load(f)

			TTL_SECONDS = 6 * 60 * 60 # 6 hour 
			retrieved_time = self.itemMapping["retrieved_at"]
			now = int(time.time())

			is_stale = (now - retrieved_time) >= TTL_SECONDS

			if is_stale:
				# Refresh once
				self.saveSixHourAve()

				# Reload once
				with open(self.sixHourAveSnapshotPath, "r", encoding="utf-8") as f:
					self.sixHourAveSnapshot = json.load(f)
		else:
			self.saveSixHourAve()

			# Reload once
			with open(self.sixHourAveSnapshotPath, "r", encoding="utf-8") as f:
				self.sixHourAveSnapshot = json.load(f)

	def saveOneDayAve(self):
		print("SENDING 24 HOUR AVE REQUEST")
		reqUrl = self.endpoint + "/24h"
		res = self.reqSession.get(reqUrl)
		res.raise_for_status()

		loadedJson = res.json()

		mappedResult = {
			"retrieved_at": int(time.time()), # UTC unix seconds
			"data": loadedJson["data"]
		}

		Path(self.oneDayAveSnapshotPath).parent.mkdir(parents=True, exist_ok=True)

		with open(self.oneDayAveSnapshotPath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadOneDayAve(self):

		if Path(self.oneDayAveSnapshotPath).exists():

			# Load existing cache
			with open(self.oneDayAveSnapshotPath, "r", encoding="utf-8") as f:
				self.oneDayAveSnapshot = json.load(f)

			TTL_SECONDS = 24 * 60 * 60 # 6 hour 
			retrieved_time = self.itemMapping["retrieved_at"]
			now = int(time.time())

			is_stale = (now - retrieved_time) >= TTL_SECONDS

			if is_stale:
				# Refresh once
				self.oneDayAveSnapshot()

				# Reload once
				with open(self.oneDayAveSnapshotPath, "r", encoding="utf-8") as f:
					self.oneDayAveSnapshot = json.load(f)
		else:
			self.saveOneDayAve()

			# Reload once
			with open(self.oneDayAveSnapshotPath, "r", encoding="utf-8") as f:
				self.oneDayAveSnapshot = json.load(f)


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

		Path(self.mappingCachePath).parent.mkdir(parents=True, exist_ok=True)

		with open(self.mappingCachePath, "w", encoding="utf-8") as f:
			json.dump(mappedResult, f, ensure_ascii=False)

	def loadMapping(self):

		if Path(self.mappingCachePath).exists():

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
		else:
			# Refresh once
			self.saveMapping()

			# Reload once
			with open(self.mappingCachePath, "r", encoding="utf-8") as f:
				self.itemMapping = json.load(f)

	
	def getLatestSnapshot(self):
		self.loadAllItemsLatest()
		return self.latestSnapshot
	
	def getItemMapping(self):
		self.loadMapping()
		return self.itemMapping
	
	def getFiveMinAveSnapshot(self):
		self.loadFiveMinAve()
		return self.fiveMinAveSnapshot
	
	def getOneHourAveSnapshot(self):
		self.loadOneHourAve()
		return self.oneHourAveSnapshot
	
	def getSixHourAveSnapshot(self):
		self.loadSixHourAve()
		return self.sixHourAveSnapshot
	
	def getOneDayAveSnapshot(self):
		self.loadOneDayAve()
		return self.oneDayAveSnapshot
	
if __name__ == '__main__':

	geapi = Geapi()
	geapi.setup()
	geapi.getLatestSnapshot()
	geapi.getItemMapping()
	geapi.getFiveMinAveSnapshot()
	geapi.getOneHourAveSnapshot()
	geapi.getSixHourAveSnapshot()
	geapi.getOneDayAveSnapshot()
	
