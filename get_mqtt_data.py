import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

MQTT_ADDRESS = "10.20.126.8"
MQTT_USER = 'cdavid'
MQTT_PASSWORD = 'cdavid'
MQTT_TOPIC = "outTopic"

mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)
    client.subscribe("#")
    client.subscribe("uuid")
    #client.subscribe("uuidReply")
    client.subscribe("log")
    client.subscribe("toESPDebug")
    client.subscribe("painlessMesh/from/gateway")

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    # setting qos to 1
    # mqtt_client.publish("uuidReply","RPIpayload",2)
    reply = "UUID recieved: " + str(msg.payload)
    #publish.single("uuidReply",reply,hostname=MQTT_ADDRESS)
    #publish.single("painlessMesh/to/toNodes",reply,hostname=MQTT_ADDRESS)
    print(msg.topic + ' ' + str(msg.payload))
    #print("  publishing : " + reply)

def on_publish(client, userdata, msg):
    print("Data published")

def main():
    #mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()

