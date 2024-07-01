""" Module for loading settings. """
import functools
import logging
import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from envyaml import EnvYAML
from pydantic.v1.utils import deep_update, unique_list

from slack_server_mock.constants import PROJECT_ROOT_PATH

logger = logging.getLogger(__name__)

_settings_folder = os.environ.get("KNOWLEDGE_BASE_SETTINGS_FOLDER", PROJECT_ROOT_PATH)

# if running in unittest, use the test profile
_test_profile = ["test"] if "tests.fixtures" in sys.modules else []

# Calculate the additional profiles from the environment variable
_additional_profiles = [
    item.strip()
    for item in os.environ.get("KNOWLEDGE_BASE_PROFILES", "").split(",")
    if item.strip()
]

active_profiles: list[str] = unique_list(
    ["default"] + _additional_profiles + _test_profile
)


def _merge_settings(settings: Iterable[dict[str, Any]]) -> dict[str, Any]:
    return functools.reduce(deep_update, settings, {})


def _load_settings_from_profile(profile: str) -> dict[str, Any]:
    if profile == "default":
        profile_file_name = "settings.yaml"
    else:
        profile_file_name = f"settings-{profile}.yaml"

    path = Path(_settings_folder) / profile_file_name
    config = EnvYAML(path).export()
    if not isinstance(config, dict):
        raise TypeError(f"Config file has no top-level mapping: {path}")
    return config


def load_active_settings() -> dict[str, Any]:
    """Load active profiles and merge them."""
    logger.info("Starting application with profiles=%s", active_profiles)
    loaded_profiles = [
        _load_settings_from_profile(profile) for profile in active_profiles
    ]
    merged: dict[str, Any] = _merge_settings(loaded_profiles)
    return merged
