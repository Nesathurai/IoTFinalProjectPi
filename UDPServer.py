# no longer being used, replaced with mqtt
# https://docs.python.org/3/library/socket.html
from socket import *
from time import sleep

# serverIP = "pi4.local"
serverIP = "allan2.local"
serverPort = 1833
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("10.20.126.8", serverPort))
# serverSocket.bind((serverIP, serverPort))
print("The server is ready to receive")

rfidDict = dict()
rfidDictRev = dict()

while 1:
    message, clientAddress = serverSocket.recvfrom(2048)
    print("recieved: ", str(message))
    print(clientAddress)
    # strip off the b' and ' at the beginning and end
    msgSplit = (str(message))[2:-1].split(";")
    print(msgSplit)
    # if expecting a reply, send a reply
    reply = "Here is your reply;end"
    replyBytes = reply.encode(encoding="utf-8")
    if msgSplit[-1] == "1":
        print(replyBytes)
        serverSocket.sendto(replyBytes, clientAddress)
    # modifiedMessage = message.upper()
    # serverSocket.sendto(modifiedMessage, clientAddress)
    sleep(1)