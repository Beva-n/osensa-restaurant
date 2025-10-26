from asyncio_mqtt import Client
import ssl, socket
from typing import Optional

def build_client(host: str, port: int,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 tls: bool = False) -> Client:
    kwargs = {
        "transport": "tcp",  # backend must use TCP, not websockets
        "client_id": f"py_backend_{socket.gethostname()}",
        "clean_session": True,
        "keepalive": 60,
    }
    if username and password:
        kwargs["username"] = username
        kwargs["password"] = password
    if tls:
        context = ssl.create_default_context()
        kwargs["tls_context"] = context
    return Client(hostname=host, port=port, **kwargs)
