import asyncio
import websockets
from websocket import create_connection
import json
from time import sleep

# For more information check out
# https://github.com/bhaptics/tact-python


# Create a websocket on the same port games use to connect
# to the bhaptics player
ws = create_connection("ws://192.168.1.53:80/ws")

# Map bhaptics vest motor ids to my vests vr motors,
# thier vest has 12 motors on each side when mine has 4.
def map_front_motors(index):
    if index in [0,1,4,5]:
        return [1, 2]
    if index in [2,3,6,7]:
        return [4,3]
    if index in [8,9,12,13,16,17]:
        return [5,6]
    if index in [10,11,14,15,18,19]:
        return [7,8]

async def server(websocket, path):
    while True:
        try:
            # Get received data from websocket
            data = await websocket.recv()


            data = json.loads(data.replace("'", "\""))
            # Check the json sent has the correct attributes.
            if 'Submit' in data:
                if 'Frame' in data['Submit'][0]:
                    # Grab the duration to turn the motors on for
                    duration = data['Submit'][0]['Frame']['DurationMillis']
                    # each frame can have multiple motors so map each to our ids
                    motors = []
                    for point in data['Submit'][0]['Frame']['DotPoints']:
                        motors += map_front_motors(point['Index'])

                    # Turn the relevant motors on
                    for motor in set(motors):
                        ws.send("on_" + str(motor))
                    # Sleep for the duration in milliseconds
                    sleep(duration/1000)
                    # Then turn all the motors off
                    for motor in set(motors):
                        ws.send("off_" + str(motor))

        except Exception as e:
            print(e)


# Create the websocket server
start_server = websockets.serve(server, "localhost", 15881)

# Start and run websocket server forever
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
