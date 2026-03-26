"""
Driver factory for Appium WebDriver creation.

Loads desired capabilities from YAML config files and creates an
Appium WebDriver session. Supports Android and iOS via the ``platform``
parameter. All sensitive values (device names, app paths) can be
overridden via environment variables.

Usage::

    from utils.driver_factory import create_driver

    driver = create_driver(platform="android")
    # ... run tests ...
    driver.quit()
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

CAPS_DIR = Path(__file__).parent.parent / "caps"
APPIUM_SERVER_URL = os.environ.get("APPIUM_SERVER_URL", "http://localhost:4723")

_ENV_OVERRIDES_ANDROID: dict[str, str] = {
    "appium:deviceName": "ANDROID_DEVICE_NAME",
    "appium:app": "ANDROID_APP_PATH",
    "appium:appPackage": "ANDROID_APP_PACKAGE",
    "appium:appActivity": "ANDROID_APP_ACTIVITY",
}

_ENV_OVERRIDES_IOS: dict[str, str] = {
    "appium:deviceName": "IOS_DEVICE_NAME",
    "appium:platformVersion": "IOS_PLATFORM_VERSION",
    "appium:app": "IOS_APP_PATH",
    "appium:bundleId": "IOS_BUNDLE_ID",
}


def _load_caps(platform: str) -> dict[str, Any]:
    """Load capabilities from YAML and apply environment variable overrides."""
    caps_file = CAPS_DIR / f"{platform.lower()}_caps.yaml"
    if not caps_file.exists():
        raise FileNotFoundError(
            f"Capabilities file not found: {caps_file}. "
            f"Expected one of: android_caps.yaml, ios_caps.yaml"
        )

    with caps_file.open() as f:
        caps: dict[str, Any] = yaml.safe_load(f) or {}

    overrides = (
        _ENV_OVERRIDES_ANDROID
        if platform.lower() == "android"
        else _ENV_OVERRIDES_IOS
    )
    for cap_key, env_var in overrides.items():
        value = os.environ.get(env_var)
        if value:
            logger.debug("Overriding %s from env var %s", cap_key, env_var)
            caps[cap_key] = value

    return caps


def create_driver(platform: str = "android") -> Any:
    """
    Create and return an Appium WebDriver for the given platform.

    Parameters
    ----------
    platform:
        ``"android"`` or ``"ios"``

    Returns
    -------
    appium.webdriver.Remote
        A connected Appium WebDriver session.

    Raises
    ------
    ImportError
        When Appium Python client is not installed.
    RuntimeError
        When the Appium server is unreachable or session creation fails.
    """
    try:
        from appium import webdriver
        from appium.options import AppiumOptions
    except ImportError as exc:
        raise ImportError(
            "Appium Python client not installed. "
            "Run: pip install Appium-Python-Client"
        ) from exc

    caps = _load_caps(platform)
    server_url = APPIUM_SERVER_URL
    logger.info(
        "Creating Appium driver — platform=%s, server=%s", platform, server_url
    )

    options = AppiumOptions().load_capabilities(caps)
    try:
        driver = webdriver.Remote(server_url, options=options)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to create Appium session for platform={platform!r} "
            f"at {server_url}: {exc}"
        ) from exc

    logger.info("Appium session created: %s", driver.session_id)
    return driver
