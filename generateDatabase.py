import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from datetime import datetime

#https://leportella.com/sqlalchemy-tutorial/
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys, select


MQTT_ADDRESS = "10.20.126.8"
MQTT_USER = 'cdavid'
MQTT_PASSWORD = 'cdavid'
MQTT_TOPIC = "outTopic"

mqtt_client = mqtt.Client()

Base = declarative_base()
engine = create_engine('sqlite:///userDatabase.sqlite', echo=True)
conn = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    uid = Column(String)
    name = Column(String)
    access = Column(String)
    lastAccessed = Column(DateTime)

    def __repr__(self):
        return f'User {self.name}'

Base.metadata.create_all(engine)

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)
    client.subscribe("#")

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    # https://www.programiz.com/python-programming/datetime/current-datetime
    # setting qos to 1
    now = datetime.now()
    message = str(msg.payload.decode())
    print(msg.topic + ' ' + str(msg.payload))
    # mqtt_client.publish("uuidReply","RPIpayload",2)
    replyAdd = "Added to database: uid = " + message + "; name = Allan Nesathurai; access = false ; date_accessed = " + now.strftime("%d/%m/%Y %H:%M:%S")
    replyDeny = "User with uid: " + message + " has been denied access. Please try again later."
    replyApproved = "User with uid: " + message + " has been approved access!"
    topSplit = str(msg.topic).split("/")
    #print(topSplit)
    if( (topSplit[0] == "to") and (topSplit[1] == "broker") ):
        #publish.single("from/broker"+topSplit[2],reply,hostname=MQTT_ADDRESS)  
        
        # check if user in database
        query = session.query(User).filter_by(uid=message) 
        # session.query(User).filter(User.id == 1).update({'name':"not john snow"})
        session.commit()
        # if not found, add to database
        if(query.count() == 0):
            accept = "False"
            print("You have 5 seconds to answer")

            i, o, e = select.select([sys.stdin], [], [], 5)

            if (i):
                accept=sys.stdin.readline().strip()
                print("You said", accept)
                
            else:
                print("You said nothing")


            # add user; change name later
            user = User(uid=message, name="Allan Nesathurai", access=accept, lastAccessed=now)
            session.add(user)
            session.commit()
            publish.single("from/broker"+topSplit[2],replyAdd,hostname=MQTT_ADDRESS)  
            print(replyAdd)
        # now, see if user has access or not 
        query = session.query(User).filter_by(uid=message,access="True")
        # user has no access, or not found
        if(query.count() == 0):
            publish.single("from/broker"+topSplit[2],replyDeny,hostname=MQTT_ADDRESS)  
            print(replyDeny)
        else:
            publish.single("from/broker"+topSplit[2],replyApproved,hostname=MQTT_ADDRESS)  
            print(replyDeny)
    print()
    #publish.single("uuidReply",reply,hostname=MQTT_ADDRESS)
    #publish.single("painlessMesh/to/toNodes",reply,hostname=MQTT_ADDRESS)
    #print(msg.topic + ' ' + (msg.payload).decode())
    
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

