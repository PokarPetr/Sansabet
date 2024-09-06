from utils.imports import asyncio, time, datetime, ClientSession
from utils.log_config import log_message
from config import PREMATCH_UPDATE_INTERVAL, LIVE_UPDATE_INTERVAL, SPORTS_IDS, MAX_CONCURRENT_REQUESTS, HEADERS
from config import PREMATCH_URLS, LIVE_URLS
from sansabet_parser import get_sansabet_odds
from pre_match_parser import parse_one_match
from utils.data_sender import send_data
from pre_match_parser import parsed_matches

async def update_odds():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with ClientSession(headers=HEADERS) as session:
        for sport_id in [SPORTS_IDS['Football'], SPORTS_IDS["Tennis"]]:
            all_urls = {
                "pre_matches": {
                    "sports_leagues": PREMATCH_URLS.get("sports_leagues", ""),
                    "parse_one_match": PREMATCH_URLS.get("parse_one_match", ""),
                    "league": PREMATCH_URLS.get("league", "")
                },
                "live": {
                    "sports_leagues": LIVE_URLS.get("all_events", ""),
                    "parse_one_match": LIVE_URLS.get("match_event", "")
                }
            }
            for key, urls in all_urls.items():
                events = await get_sansabet_odds(session, sport_id, urls)
                url = urls.get('parse_one_match', PREMATCH_URLS["parse_one_match"])
                tasks = [parse_one_match(event, session, url, semaphore) for event in events]
                await asyncio.gather(*tasks)


async def update_sansabet_odds_periodically(interval=PREMATCH_UPDATE_INTERVAL):
    print("Sansabet odds updater started", file=open('log_sansa.txt', 'a'))
    while True:
        start_time = time.time()
        try:
            await asyncio.shield(update_odds())
            parsed_matches_new = []
            for match in parsed_matches.values():
                if (datetime.now().timestamp() - match['time']) < 15:
                    parsed_matches_new.append(match)
            log_message('info',
                f"Коэффициенты Sansabet обновлены. Всего матчей: {len(ALL_MATCHES)}, Обработанных матчей: {len(parsed_matches_new)}")
            print(
                f"Коэффициенты Sansabet обновлены. Всего матчей: {len(ALL_MATCHES)}, Обработанных матчей: {len(parsed_matches_new)}",
                datetime.now(), file=open('log_sansa.txt', 'a'))
        except Exception as e:
            log_message('error', f"Ошибка при обновлении коэффициентов Sansabet: {e}")
            print(f"Ошибка при обновлении коэффициентов Sansabet: {e}",
                  datetime.now(), file=open('log_sansa.txt', 'a'))

        elapsed_time = time.time() - start_time
        sleep_time = max(0, interval - elapsed_time)
        await asyncio.sleep(sleep_time)
"""
   Entry point of the application. It schedules periodic updates for fetching and processing odds data.
"""
if __name__ == "__main__":
    asyncio.run(update_sansabet_odds_periodically())
    # asyncio.run(send_data(parsed_matches))




























# import asyncio
# import websockets
# import logging
#
# logging.basicConfig(level=logging.INFO)
#
# async def echo(websocket, path):
#     async for message in websocket:
#         logging.info(f"Received message: {message}")
#         await websocket.send("Data received")
#
# async def main():
#     server = await websockets.serve(echo, "localhost", 8765)
#     await server.wait_closed()
#
# if __name__ == "__main__":
#     asyncio.run(main())