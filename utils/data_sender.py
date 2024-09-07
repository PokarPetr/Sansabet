from .imports import asyncio, websockets, json
from .log_config import log_message
from config import HOST, PORT


async def send_data(data):
    """
    Отправляет данные на заданный WebSocket URI.
    :param data: Данные для отправки в формате словаря
    """

    uri = f"ws://{HOST}:{PORT}"
    async with websockets.connect(uri) as websocket:
        try:

            await websocket.send(json.dumps(data))
            log_message('info', f"Data sent to {uri}: {data}")

            response = await websocket.recv()
            log_message('info', f"Response from {uri}: {response}")

        except websockets.exceptions.ConnectionClosedError as e:
            log_message('error', f"WebSocket connection closed with error: {e}")
        except Exception as e:
            log_message('error', f"Unexpected error occurred while sending data: {e}")


if __name__ == "__main__":
    async def main():
        data = {"example": "data"}
        await send_data(data)

    asyncio.run(main())