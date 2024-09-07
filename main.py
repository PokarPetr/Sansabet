from utils.imports import asyncio, datetime, ClientSession, time
from utils.log_config import log_message
from config import PREMATCH_UPDATE_INTERVAL, LIVE_UPDATE_INTERVAL, SPORTS_IDS, MAX_CONCURRENT_REQUESTS, HEADERS
from parsers.sansabet_parser import get_sansabet_matches
from parsers.sansabet_parser import parse_one_match
from utils.data_sender import send_data

parsed_matches = {
    "PreMatch": {},  # Для хранения предматчевых данных
    "Live": {}       # Для хранения live-данных
}
previous_state = {  # Сохранение предыдущих состояний матчей для сравнения
    "PreMatch": {},
    "Live": {}
}

ALL_MATCHES = {}


async def get_updated_matches():
    updated_matches = {"PreMatch": [], "Live": []}
    for mode in ["PreMatch", "Live"]:
        for event_id, match_data in parsed_matches[mode].items():
            if event_id not in previous_state[mode] or previous_state[mode][event_id] != match_data:
                updated_matches[mode].append(match_data)

        previous_state[mode] = parsed_matches[mode].copy()
    return updated_matches


async def send_updated_matches(interval):
    while True:
        start_time = time.time()
        updated_matches = await get_updated_matches()

        if updated_matches["PreMatch"] or updated_matches["Live"]:
            try:
                await asyncio.shield(send_data(updated_matches))
            except Exception as e:
                log_message('error', f"Ошибка при обновлении коэффициентов Sansabet: {e}")

        elapsed_time = time.time() - start_time
        await asyncio.sleep(max(0, interval - elapsed_time))


async def update_odds(mode):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with ClientSession(headers=HEADERS) as session:
        for sport_id in [SPORTS_IDS['Football'], SPORTS_IDS["Tennis"]]:
            events = await get_sansabet_matches(session, sport_id, mode)
            tasks = [parse_one_match(event, session, mode, semaphore) for event in events]
            await asyncio.gather(*tasks)


async def update_sansabet_odds_periodically(interval, mode):
    while True:
        start_time = time.time()
        try:
            await asyncio.shield(update_odds(mode))
        except Exception as e:
            log_message('error', f"Ошибка при обновлении коэффициентов Sansabet: {e}")

        elapsed_time = time.time() - start_time
        await asyncio.sleep(max(0, interval - elapsed_time))


async def run_tasks():
    """
    Функция для запуска фоновых задач с разными интервалами обновления.
    """
    try:
        tasks = [
            asyncio.create_task(update_sansabet_odds_periodically(PREMATCH_UPDATE_INTERVAL, "PreMatch")),  # Раз в час
            asyncio.create_task(update_sansabet_odds_periodically(LIVE_UPDATE_INTERVAL, "Live")),  # Раз в минуту
            asyncio.create_task(send_updated_matches(LIVE_UPDATE_INTERVAL))  # Раз в минуту
        ]
        await asyncio.gather(*tasks)
    except Exception as e:
        log_message('error', f"Ошибка в основном процессе: {e}")
    finally:
        log_message('info', "Завершение программы")


if __name__ == "__main__":
    asyncio.run(run_tasks())




























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