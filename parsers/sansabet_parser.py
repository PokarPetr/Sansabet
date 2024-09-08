from utils.imports import asyncio, time, datetime, timezone
from utils.log_config import log_message
from config import SPORTS_IDS, PREMATCH_URLS, NEED_TIME_PARS, LIVE_URLS
from utils.network import fetch_with_retry
from .pre_match_parser import parse_one_pre_match
from .live_match_parser import parse_one_live_match

all_urls = {
                "PreMatch": {
                    "sports_leagues": PREMATCH_URLS.get("sports_leagues", ""),
                    "parse_one_match": PREMATCH_URLS.get("parse_one_match", ""),
                    "league": PREMATCH_URLS.get("league", "")
                },
                "Live": {
                    "sports_leagues": LIVE_URLS.get("all_events", ""),
                    "parse_one_match": LIVE_URLS.get("match_event", "")
                }
            }

async def sport_by_id(sport_id):
    for sport, sid in SPORTS_IDS.items():
        if sid == sport_id:
            return sport


async def parse_one_match(event, session, mode, semaphore):
    async with semaphore:
        urls = all_urls.get(mode, {})
        if mode == "Live":
            event = await parse_one_live_match(session, event, urls)
            return event
        url = urls['parse_one_match']
        one_match = await parse_one_pre_match(session, event, url, semaphore)
        # log_message('info', f"match ID: {one_match['match_id']}")
        return one_match


async def get_pre_matches_leagues_ids(session, sport_id, url):
    data = {
        "filter": "0",
        "activeStyle": "img/sports"
    }
    sports = await fetch_with_retry(session, url, data)  # URL1
    leagues_ids = []
    if sports:
        for sport in sports:
            if 'SID' not in sport or sport['SID'] != sport_id:
                continue

            if 'L' not in sport or not sport['L']:
                continue

            for league in sport['L']:
                leagues_ids.append(league['LID'])
    return leagues_ids


async def get_pre_matches(session, sport_id, urls):
    url = urls['sports_leagues']
    leagues_ids = await get_pre_matches_leagues_ids(session, sport_id, url)
    data = {
        "LigaID": leagues_ids,
        "filter": "0",
        "parId": 0
    }
    url = urls['league']
    leagues = await fetch_with_retry(session, url, data)
    matches = []

    if leagues:
        for league in leagues:
            for match_data in league.get('P'):
                teams = match_data.get('PN', ' : ').split(' : ')

                di_str = match_data.get('DI')
                if len(di_str) > 26 :
                    fd = di_str[:26]
                    ld = di_str[-6:]
                    di_str_fixed = fd + ld
                else:
                    di_str_fixed = di_str

                start_at = datetime.fromisoformat(di_str_fixed)
                utc_time = start_at.astimezone(timezone.utc)

                match = {
                    "match_id": match_data.get('PID'),
                    "league": league.get('NW', ''),
                    "home_team": teams[0],
                    "away_team": teams[1],
                    "sport": await sport_by_id(sport_id),
                    "country": league.get('NG', ''),
                    "start_time": utc_time.strftime("%Y-%m-%d %H:%M:%S"),
                }

                if (utc_time - datetime.now(timezone.utc)).total_seconds() <= NEED_TIME_PARS * 3600:
                    if (not "BetBuilder" in match['home_team']) and (not "BetBuilder" in match['away_team']):
                        matches.append(match)

    return matches

async def get_live_matches(session, urls):
    url = urls['sports_leagues'].format(0)
    matches = await fetch_with_retry(session, url, None, 2, "GET")
    return matches


async def parse_matches(session, sport_id, mode):
    urls = all_urls.get(mode, {})

    if mode == "Live":
        return await get_live_matches(session, urls)
    else:
        pred_matches = await get_pre_matches(session, sport_id, urls)
        return pred_matches


async def get_sansabet_matches(session, sport_id, mode):

    new_matches = {}
    log_message('info', f"session: {session}, sport_id: {sport_id} , mode: {mode}")
    while True:
        try:
            new_matches = await parse_matches(session, sport_id, mode)
            break
        except Exception as e:
            log_message('error', f"Error occurred while parsing matches: {e}")
            print(f"Error occurred while parsing matches: {e}",
                  datetime.now(), file=open('log_sansa.txt', 'a'))
            continue

    return new_matches
