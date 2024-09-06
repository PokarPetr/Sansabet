from utils.imports import asyncio, time, datetime, timezone
from utils.log_config import log_message
from config import PREMATCH_UPDATE_INTERVAL, LIVE_UPDATE_INTERVAL, SPORTS_IDS, PREMATCH_URLS, NEED_TIME_PARS
from utils.network import fetch_with_retry
from pre_match_parser import parsed_matches

ALL_MATCHES = {}

async def sport_by_id(sport_id):
    for sport, sid in SPORTS_IDS.items():
        if sid == sport_id:
            return sport

async def parse_leagues_by_sport(session, sport_id, url):
    data = {
        "filter": "0",
        "activeStyle": "img/sports"
    }
    sports = await fetch_with_retry(session, url, data)  # URL1
    leagues_ids = []

    if sports:
        for sport in sports:
            if sport['SID'] != sport_id:
                continue

            for league in sport['L']:
                leagues_ids.append(league['LID'])

    return leagues_ids


async def parse_matches(session, sport_id, urls):
    url = urls.get('sports_leagues', PREMATCH_URLS['sports_leagues'])
    leagues_ids = await parse_leagues_by_sport(session, sport_id, url)
    data = {
        "LigaID": leagues_ids,
        "filter": "0",
        "parId": 0
    }
    url = urls.get('league', PREMATCH_URLS["league"])
    leagues = await fetch_with_retry(session, url, data)
    matches = {}

    if leagues:
        for league in leagues:
            for match_data in league['P']:
                teams = match_data['PN'].split(' : ')

                start_at = datetime.fromisoformat(match_data['DI'])
                utc_time = start_at.astimezone(timezone.utc)

                match = {
                    "match_id": match_data['PID'],
                    "league": league['NW'],
                    "home_team": teams[0],
                    "away_team": teams[1],
                    "sport": await sport_by_id(sport_id),
                    "country": league['NG'],
                    "start_time": utc_time.strftime("%Y-%m-%d %H:%M:%S"),

                }
                if (utc_time - datetime.now(timezone.utc)).total_seconds() <= NEED_TIME_PARS * 3600:
                    if (not "BetBuilder" in match['home_team']) and (not "BetBuilder" in match['away_team']):
                        matches[match_data['PID']] = match

    return matches


async def get_sansabet_odds(session, sport_id, urls):
    global ALL_MATCHES, parsed_matches
    while True:
        try:
            new_matches = await parse_matches(session, sport_id, urls)
            break
        except Exception as e:
            log_message('error', "Error occurred while parsing matches: {e}")
            print(f"Error occurred while parsing matches: {e}",
                  datetime.now(), file=open('log_sansa.txt', 'a'))
            continue

    if not new_matches:
        # return []
        return parsed_matches

    # ALL_MATCHES.update(new_matches)
    #
    # # Remove matches from ALL_MATCHES and parsed_matches that are no longer present in the new data
    # ALL_MATCHES = {k: v for k, v in
    #                ALL_MATCHES.items()}  # if k in new_matches
    # parsed_matches = {k: v for k, v in
    #                   parsed_matches.items()}  # if k in new_matches
    #
    # # Process new matches
    # await process_matches(new_matches)

    return parsed_matches
