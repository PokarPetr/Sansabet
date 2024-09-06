# URLs for pre-match and live events
PREMATCH_URLS = {
    "sports_leagues": "https://sansabet.com/Oblozuvanje.aspx/GetSportoviSoLigi",
    "most_played": "https://sansabet.com/Oblozuvanje.aspx/GetNajigrani",
    "league": "https://sansabet.com/Oblozuvanje.aspx/GetLiga",
    "parse_one_match": "https://sansabet.com/Oblozuvanje.aspx/GetTipoviV2",
}

LIVE_URLS = {
    "all_events": "https://apilive.sansabet.com/api/LiveOdds/GetAll?SLID={}",
    "match_event": "https://apilive.sansabet.com/api/LiveOdds/GetByParIDs?SLID={}&ParIDs={}"
}

# HTTP headers used in both pre-match and live requests
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Origin": "https://sansabet.com",
    "Referer": "https://sansabet.com/",
    "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Linux"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# Sports IDs for pre-match parsing
SPORTS_IDS = {
    'Football': 0,
    'Special games': 51,
    'Basketball': 22,
    'Tennis': 37,
    'Handball': 7,
    'Volleyball': 38,
    'Water polo': 9,
    'American football': 41,
    'Baseball': 39,
    'Snooker': 43,
    'Darts': 44,
    'Motor Sport': 47,
    'Martial arts': 40,
    'eSport': 52,
    'Pobednik': 25
}

# Timeframe for event parsing (24 hours for pre-match events)
NEED_TIME_PARS = 24

# Proxies list and proxy cycling for both pre-match and live parsing
PROXIES = [
    "http://UM7mgP:lCYt0wOU7Z@45.86.0.92:1050",
    "http://UM7mgP:lCYt0wOU7Z@188.130.129.231:1050",
    "http://UM7mgP:lCYt0wOU7Z@188.130.136.143:1050",
    "http://UM7mgP:lCYt0wOU7Z@109.248.139.122:1050",
    "http://UM7mgP:lCYt0wOU7Z@109.248.143.160:1050",
    "http://UM7mgP:lCYt0wOU7Z@109.248.166.233:1050",
    "http://UM7mgP:lCYt0wOU7Z@46.8.16.88:1050",
    "http://UM7mgP:lCYt0wOU7Z@46.8.110.173:1050",
    "http://UM7mgP:lCYt0wOU7Z@46.8.17.231:1050",
    "http://UM7mgP:lCYt0wOU7Z@94.158.190.9:1050",
]

# Concurrency settings
MAX_CONCURRENT_REQUESTS = 200

# Port and update intervals (can be used for scheduling tasks)
# These values can be updated depending on specific requirements
HOST = 'localhost'
PORT = 8765
# DATA_PORT = 8080  # Port for sending parsed data to localhost
PREMATCH_UPDATE_INTERVAL = 3600  # Update interval for pre-match events (in seconds)
LIVE_UPDATE_INTERVAL = 30  # Update interval for live events (in seconds)

# Game list for live parsing
SLID_ALL = 0  # Default SLID for live parsing
list_games = {}  # Dictionary to store live games data


