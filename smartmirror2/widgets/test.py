import asyncio
import socket

async def handle_client(reader, writer):
    while True:
        data = (await reader.read(255)).decode('utf8')
        if not data:
            break
        print(data)
        writer.write('OK'.encode('utf8'))
        await writer.drain()
    writer.close()

loop = asyncio.get_event_loop()
loop.create_task(asyncio.start_server(handle_client, '127.0.0.1', 9086))
loop.run_forever()

"""LOCALHOST = '127.0.0.1'
LOCALPORT = 9086

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

sock.bind((LOCALHOST, LOCALPORT))
sock.listen(1)
conn, addr = sock.accept()
print('Connected')
while True:
    data = conn.recv(1024)
    print(data, addr)
    if not data:
        break"""
print('ALLES')