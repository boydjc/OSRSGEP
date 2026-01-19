from api import Geapi
import time

class GeController:

    def __init__(self):
        self.geapi = Geapi()

    # grabs the top x number of widest spreads
    def findWidestSpreads(self, limit=50):

        latestSnapshot = self.geapi.getLatestSnapshot()

        data = latestSnapshot['data']

        now = int(time.time())

        MAX_AGE_SECONDS = 5 * 60 # 5 minutes

        rows = []

        for itemId, q in data.items():

            high = q.get('high')
            low = q.get('low')

            if not high or not low or high <= 0 or low <= 0:
                continue

            spread = high - low
            if spread <= 0:
                continue

            mid = (high + low) / 2
            spreadPct = spread/mid

            # provide a freshness filter (prevents fake wide spreads)
            highTime = q.get('highTime')
            lowTime = q.get('lowTime')

            if (now - highTime) > MAX_AGE_SECONDS or (now - lowTime) > MAX_AGE_SECONDS:
                continue

            # search for the item in the mapping to get the name

            itemDetails = self.geapi.searchMapping(itemId)

            rows.append({
                "item_id": int(itemId),
                "item_name": itemDetails.get('name'),
                "item_limit": itemDetails.get('limit'),
                "low": low,
                "high": high,
                "spreadPct": spreadPct
            })

        rows.sort(key=lambda r: r["spreadPct"], reverse=True)
        return rows[:limit]


if __name__ == "__main__":
    geController = GeController()

    widestSpreads = geController.findWidestSpreads()
    for item in widestSpreads:
        print(item)