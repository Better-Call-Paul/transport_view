from realTimeParse import getStationCongestion

# Constants
BASE_TICKET_PRICE = 2.90
MAX_PRICE_FLUCTUATION = 0.50  # up to 50 cents fluctuation for minor adjustments
MAX_DECREASE = 0.50  # Maximum decrease in price
MIN_DECREASE = 0.10  # Minimum decrease in price


# Weights
WEIGHT_REAL_TIME = 0.3  # 20% weight for real-time congestion
WEIGHT_HISTORICAL = 0.7  # 80% weight for historical congestion


def calculateCombinedCongestion(realTimeScore=4.0, historicalScore=10.0):
    return (float(realTimeScore) * WEIGHT_REAL_TIME) + (float(historicalScore) * WEIGHT_HISTORICAL)

def getPriceAdjustment(combinedCongestion):
    # print(f"CombinedCongestion: {combinedCongestion}")
    if combinedCongestion >= 10:  # Hypothetical threshold for high congestion
        return MAX_PRICE_FLUCTUATION
    elif combinedCongestion >= 5:  # Moderate congestion
        return MAX_PRICE_FLUCTUATION * 0.5
    elif combinedCongestion <= 2:
        # print("returned this")
        return -MAX_DECREASE  # Maximum discount for very low congestion
    elif combinedCongestion < 5:
        return -MIN_DECREASE  # Some discount for moderate congestion
    else:
        return 0  # No discount for high congestion

def calculateDynamicPrice(congestionScore):
    """Calculate the dynamic price based on the congestion score."""
    adjustment = getPriceAdjustment(congestionScore)
    dynamicPrice = BASE_TICKET_PRICE + adjustment
    return round(dynamicPrice, 2)


def getTicketPrice(stationId):
    """Fetch the current congestion score and compute the dynamic ticket price."""
    stationCongestion = getStationCongestion(stationId)[1]
    # print(stationCongestion, type(stationCongestion))
    # historicalCongestion = getHistoricalCongestion(stationId)
    congestionScore = calculateCombinedCongestion(stationCongestion)  # Assume this function fetches the current score
    return calculateDynamicPrice(congestionScore)


# print(getTicketPrice("127"))