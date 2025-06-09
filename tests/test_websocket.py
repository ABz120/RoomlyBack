import asyncio
import websockets

async def test_websocket():
    offer_id = input("offer_id: ")
    uri = f"ws://127.0.0.1:8000/api/hotels/ws/rooms/offers/{offer_id}"
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                print(message)
    except websockets.ConnectionClosed:
        print(f"Connection closed for offer_id {offer_id}")
    except Exception as e:
        print(f"Error for offer_id {offer_id}: {e}")

asyncio.run(test_websocket())