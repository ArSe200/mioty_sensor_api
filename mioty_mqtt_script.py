# /usr/bin/env

import paho.mqtt.client as paho
import json
from time import sleep

DEBUG = True
MQTT_IP = "192.168.10.177"
MQTT_PORT = 1883


def on_connect(client, userdata, flags, reason_code, properties):
    if DEBUG:
        print(f"\nConnected\n    Result code: {reason_code}")


def on_message(client, userdata, message):
    if not message.retain:
        basestation = json.loads(message.payload)["baseStations"][0]

        rssi = basestation["rssi"]
        eqSnr = basestation["eqSnr"]
        snr = basestation["snr"]

        if DEBUG:
            print(f"\nReceived data:")
            print("    rssi: ", end="")
            print(rssi)
            print("    eqSnr: ", end="")
            print(eqSnr)
            print("    snr: ", end="")
            print(snr)
            print("\n")

        print([int(rssi), abs(int(round(rssi - int(rssi), 2) * 100))])

        payload = {
            "data": [int(rssi), abs(int(round(rssi - int(rssi), 2) * 100))],
            "format": 0,
            "presched":True
        }

        client.publish(
            f"{"/".join(message.topic.split("/")[:3])}/downlink",
            json.dumps(payload),
        )


if __name__ == "__main__":
    client = paho.Client(
        client_id="py_mqtt_client",
        userdata=None,
        transport="tcp",
        protocol=paho.MQTTv5,
    )

    client.connect(MQTT_IP, port=MQTT_PORT)

    client.on_connect = on_connect
    client.on_message = on_message

    client.subscribe(f"mioty/00-00-00-00-00-00-00-00/+/uplink")

    client.loop_start()

    while True:
        sleep(1)
