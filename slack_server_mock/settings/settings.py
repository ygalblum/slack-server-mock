""" Settings for the application """
from pydantic import BaseModel, Field

from slack_server_mock.settings.settings_loader import load_active_settings


class HttpServer(BaseModel):
    """ Settings for the HTTP Server """
    port: int = Field(
        8888,
        description="HTTP Server Listening port"
    )


class WebSocketServer(BaseModel):
    """ Settings for the WebSockets Server """
    port: int = Field(
        3001,
        description="HTTP Server Listening port"
    )


class Actor(BaseModel):
    """ Settings for the Actor """
    port: int = Field(
        8080,
        description="Actor HTTP Server Listening port"
    )


class Settings(BaseModel):
    """ Application Settings """
    http_server: HttpServer
    websocket_server: WebSocketServer
    actor: Actor


# This is visible just for DI or testing purposes.
# Use dependency injection instead.
unsafe_typed_settings = Settings(**load_active_settings())
