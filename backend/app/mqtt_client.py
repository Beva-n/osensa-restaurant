from asyncio_mqtt import Client
import socket

def build_client(host: str, port: int) -> Client:
    return Client(
        hostname=host,
        port=port,
        transport="tcp",                       # backend uses TCP, not websockets
        client_id=f"py_backend_{socket.gethostname()}",
        clean_session=True,
        keepalive=60,
    )
