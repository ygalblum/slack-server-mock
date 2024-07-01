""" Global injector for the application """
from injector import Injector

from slack_server_mock.settings.settings import Settings, unsafe_typed_settings


def _create_application_injector() -> Injector:
    _injector = Injector(auto_bind=True)
    _injector.binder.bind(Settings, to=unsafe_typed_settings)
    return _injector


# Global injector for the application.
global_injector: Injector = _create_application_injector()
