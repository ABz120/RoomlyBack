import asyncio
import websockets

async def test_websocket():
    uri = "ws://127.0.0.1:8000/api/hotels/ws/rooms/offers/2"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(message)

asyncio.run(test_websocket())