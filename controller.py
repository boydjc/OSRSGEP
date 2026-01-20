from api import Geapi
import time
from datetime import datetime

class GeController:

    def __init__(self):
        self.geapi = Geapi()

    def findWidestSpreads(self, limit=50):

        latestSnapshot = self.geapi.getLatestSnapshot()
        data = latestSnapshot["data"]

        now = int(time.time())
        MAX_AGE_SECONDS = 5 * 60  # 5 minutes

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

            spread = high - low
            if spread <= 0:
                continue

            # Freshness 
            highTime = q.get("highTime")
            lowTime  = q.get("lowTime")
            if not isinstance(highTime, int) or not isinstance(lowTime, int):
                continue
            if (now - highTime) > MAX_AGE_SECONDS or (now - lowTime) > MAX_AGE_SECONDS:
                continue

            # After-tax economics (assume you sell at low)
            tax = GE_TAX_RATE * low
            netProfit = spread - tax
            if netProfit <= 0:
                continue

            # Percent metrics
            mid = (high + low) / 2
            spreadPct = spread / mid

            # After-tax percent edge: netProfit relative to mid (or relative to buy price)
            netSpreadPct = netProfit / mid

            # mapping lookup
            itemDetails = self.geapi.searchMapping(itemId)

            lastTradeTime = max(highTime, lowTime)

            rows.append({
                "item_id": int(itemId),
                "item_name": itemDetails.get("name"),
                "item_limit": itemDetails.get("limit"),
                "low": low,
                "high": high,
                "spreadPct": spreadPct,
                "netProfit": netProfit,
                "netSpreadPct": netSpreadPct,
                "lastTradeReadable": datetime.fromtimestamp(lastTradeTime).strftime("%H:%M:%S"),
                "lastTradeTime": lastTradeTime
            })

        # Sort by after-tax percent edge, then recency
        rows.sort(key=lambda r: (r["netSpreadPct"], r["lastTradeTime"]), reverse=True)
        return rows[:limit]
    
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


if __name__ == "__main__":
    geController = GeController()

    widestSpreads = geController.findWidestSpreads()
    for item in widestSpreads:
        print(item)