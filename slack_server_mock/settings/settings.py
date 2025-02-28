""" Settings for the application """
from pydantic import BaseModel, Field

from slack_server_mock.settings.settings_loader import load_active_settings


class SlackServer(BaseModel):
    """ Slack Server """
    http_port: int = Field(
        8888,
        description="Mock Slack HTTP Server Listening port"
    )

    websocket_port: int = Field(
        3001,
        description="Mock Slack Websocket Server Listening port"
    )

    channels_path: str = Field(
        None,
        description="Path to a file containing the list of conversations"
    )

    response_data_path: str = Field(
        None,
        description="Path to a directory structure containing response replies"
    )


class Actor(BaseModel):
    """ Settings for the Actor """
    port: int = Field(
        8080,
        description="Actor HTTP Server Listening port"
    )


class Settings(BaseModel):
    """ Application Settings """
    slack_server: SlackServer
    actor: Actor


# This is visible just for DI or testing purposes.
# Use dependency injection instead.
unsafe_typed_settings = Settings(**load_active_settings())
