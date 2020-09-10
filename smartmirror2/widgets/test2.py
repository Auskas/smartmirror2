import socket

LOCALHOST = '127.0.0.1'
LOCALPORT = 9086

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((LOCALHOST, LOCALPORT))
MESSAGE = b"Hello, World!"
sock.send(MESSAGE)
#while True:
    #data = sock.recv(1024)
    #if data.decode('utf-8') == 'OK':
        #print(data)
        #break

print('SENT!')
sock.close()