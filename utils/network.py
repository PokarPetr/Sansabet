from .imports import ClientError, ClientSession, time, json, asyncio, traceback, random
from config import PROXIES
from .log_config import log_message


async def fetch(session: ClientSession, url: str, data: dict = None, proxy: str = None, method: str = "POST",
                timeout: int = 3):
    """
    Функция для выполнения запроса с использованием указанного метода, URL, данных и прокси.

    :param session: Сессия aiohttp для выполнения запроса
    :param url: URL, на который будет отправлен запрос
    :param data: Данные, отправляемые в запросе (если есть)
    :param proxy: Прокси, через который будет выполнен запрос (если указано)
    :param method: HTTP-метод (POST или GET)
    :param timeout: Тайм-аут для запроса
    :return: Ответ в формате JSON или None при ошибке
    """
    try:
        start_time = time.time()
        if method == "POST":
            async with session.post(url, json=data, proxy=proxy, timeout=timeout) as response:
                response.raise_for_status()
                content = await response.json()
        elif method == "GET":
            async with session.get(url, proxy=proxy, timeout=timeout) as response:
                response.raise_for_status()
                content = await response.json()
        else:
            log_message('error', f"Unsupported HTTP method: {method}")
            return None

        elapsed_time = time.time() - start_time
        log_message('info', f"Request to {url} completed in {elapsed_time:.2f} seconds using proxy {proxy}")
        return content
    except asyncio.TimeoutError:
        log_message('warning', f"Timeout error occurred with proxy {proxy} for URL {url}")
    except ClientError as e:
        log_message('error', f"HTTP error occurred with proxy {proxy} for URL {url}: {e}")
    except json.JSONDecodeError:
        log_message('error', f"JSON decode error occurred with proxy {proxy} for URL {url}")
    except Exception as e:
        log_message('error', f"Unexpected error occurred with proxy {proxy} for URL {url}: {e}")
        log_message('debug', f"Full traceback: {traceback.format_exc()}")
    return None


async def fetch_with_retry(session: ClientSession, url: str, data: dict = None, max_retries: int = 2,
                           method: str = "POST"):
    """
    Функция для выполнения запроса с повторными попытками в случае неудачи.

    :param session: Сессия aiohttp для выполнения запроса
    :param url: URL, на который будет отправлен запрос
    :param data: Данные, отправляемые в запросе (если есть)
    :param max_retries: Максимальное количество попыток выполнения запроса
    :param method: HTTP-метод (POST или GET)
    :return: Ответ в формате JSON или None при ошибке
    """
    for attempt in range(max_retries):
        proxy = random.choice(PROXIES)
        result = await fetch(session, url, data, proxy, method)
        if result is not None:
            return result
        log_message('warning', f"Attempt {attempt + 1}/{max_retries} failed for URL {url}")

    log_message('error', f"All {max_retries} attempts failed for URL {url}")
    return None
