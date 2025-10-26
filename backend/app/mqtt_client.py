from asyncio_mqtt import Client
import ssl
from typing import Optional

def build_client(host: str, port: int,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 tls: bool = False) -> Client:
    kwargs = {"transport": "tcp"}  # force classic TCP, not websockets
    if username and password:
        kwargs["username"] = username
        kwargs["password"] = password
    if tls:
        context = ssl.create_default_context()
        kwargs["tls_context"] = context
    return Client(hostname=host, port=port, **kwargs)