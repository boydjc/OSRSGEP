from api import Geapi
import time
from datetime import datetime
import pandas as pd

class GeController:

    def __init__(self):
        self.geapi = Geapi()

    def findWidestSpreads(self, limit=50):

        latestSnapshot = self.geapi.getLatestSnapshot()
        data = latestSnapshot["data"]

        now = int(time.time())

        GE_TAX_RATE = 0.02

        rows = []

        for itemId, q in data.items():

            high = q.get("high")
            low  = q.get("low")

            # Guard against missing / invalid prices
            if not isinstance(high, (int, float)) or not isinstance(low, (int, float)):
                continue
            if high <= 0 or low <= 0:
                continue

            # assume we buy at low + 1 and sell at high - 1
            spread = (high-1) - (low+1)
            if spread <= 0:
                continue

            # Freshness 
            highTime = q.get("highTime")
            lowTime  = q.get("lowTime")
            if not isinstance(highTime, int) or not isinstance(lowTime, int):
                continue

            # After-tax economics (assume you sell at high-1)
            # this ensures only things that we would profit from AFTER being tax is shown
            tax = GE_TAX_RATE * (high-1)
            netProfit = spread - tax
            if netProfit <= 0:
                continue

            # Percent metrics
            mid = (high + low) / 2
            spreadPct = spread / mid

            # After-tax percent edge: netProfit relative to mid (or relative to buy price)
            netSpreadPct = netProfit / mid

            # mapping lookup
            itemDetails = self.searchMapping(itemId)

            # five minute average
            fiveMinuteAverage = self.searchFiveMinuteAveSnapshot(itemId)

            lastTradeTime = max(highTime, lowTime)

            if(fiveMinuteAverage):
                fiveMinLowVol = None if "lowPriceVolume" not in fiveMinuteAverage.keys() else fiveMinuteAverage.get("lowPriceVolume")
                fiveMinHighVol = None if "highPriceVolume" not in fiveMinuteAverage.keys() else fiveMinuteAverage.get("highPriceVolume")

                fiveMinVol = None

                # Filter that the 5 minute volume is at least 50% of the limit
                if fiveMinLowVol and fiveMinHighVol:
                    fiveMinVol = fiveMinLowVol + fiveMinHighVol

                    item_limit = itemDetails.get("limit")

                    if item_limit and fiveMinVol:
                        
                        fiveMinVolPct = fiveMinVol / item_limit

                        if fiveMinVolPct >= .5:
                            rows.append({
                                "item_id": int(itemId),
                                "item_name": itemDetails.get("name"),
                                "item_limit": itemDetails.get("limit"),
                                "low": low,
                                "vol (5m)": fiveMinVol,
                                "high": high,
                                "netSpreadPct": round(netSpreadPct, 2),
                                "lastTradeReadable": datetime.fromtimestamp(lastTradeTime).strftime("%H:%M:%S"),
                                "lastTradeTime": lastTradeTime
                            })

        # Sort by after-tax percent edge, then recency
        rows.sort(key=lambda r: (r["item_limit"], r["netSpreadPct"], r["vol (5m)"], r["lastTradeTime"],), reverse=True)
        return pd.DataFrame(rows[:limit])
    
    def searchMapping(self, itemId):

        itemMapping = self.geapi.getItemMapping()

        itemId = int(itemId)
        for item in itemMapping["items"]:
            if item["id"] == itemId:
                return item
        return None
    
    def searchLatestSnapshot(self, itemId):

        latestSnapshot = self.geapi.getLatestSnapshot()

        return latestSnapshot["data"].get(str(itemId))
    
    def searchFiveMinuteAveSnapshot(self, itemId):

        fiveMinuteAveSnapshot = self.geapi.getFiveMinAveSnapshot()

        return fiveMinuteAveSnapshot["data"].get(str(itemId))
    
    def searchOneHourAveSnapshot(self, itemId):

        oneHourAveSnapshot = self.geapi.getOneHourAveSnapshot()

        return oneHourAveSnapshot["data"].get(str(itemId))



if __name__ == "__main__":
    geController = GeController()

    widestSpreads = geController.findWidestSpreads()
    print(widestSpreads)

    #latestSnapshotItem = geController.searchLatestSnapshot(30771)

    #print(latestSnapshotItem)

    
