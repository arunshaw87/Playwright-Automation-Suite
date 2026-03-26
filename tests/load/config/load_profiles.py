"""
Load test profiles — define user counts, spawn rates, and durations
for each test scenario type.

Usage::

    from config.load_profiles import SmokeProfile, StressProfile, get_profile

    profile = get_profile("smoke")
    # profile.users, profile.spawn_rate, profile.run_time
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadProfile:
    """Base load profile configuration."""

    name: str
    users: int
    spawn_rate: int
    run_time: str
    description: str


SMOKE = LoadProfile(
    name="smoke",
    users=5,
    spawn_rate=1,
    run_time="1m",
    description="Quick sanity check — 5 users, 1 minute",
)

SOAK = LoadProfile(
    name="soak",
    users=50,
    spawn_rate=5,
    run_time="30m",
    description="Sustained load — 50 users for 30 minutes to detect memory leaks",
)

STRESS = LoadProfile(
    name="stress",
    users=200,
    spawn_rate=10,
    run_time="10m",
    description="Ramp to 200 users over ~20s, hold for 10 minutes",
)

SPIKE = LoadProfile(
    name="spike",
    users=500,
    spawn_rate=100,
    run_time="5m",
    description="Sudden spike to 500 users to test auto-scaling behaviour",
)

_PROFILES: dict[str, LoadProfile] = {
    p.name: p for p in [SMOKE, SOAK, STRESS, SPIKE]
}


def get_profile(name: str) -> LoadProfile:
    """Return the named LoadProfile. Raises ValueError for unknown names."""
    try:
        return _PROFILES[name.lower()]
    except KeyError:
        available = ", ".join(_PROFILES)
        raise ValueError(
            f"Unknown load profile {name!r}. Available: {available}"
        )


def list_profiles() -> list[LoadProfile]:
    """Return all registered load profiles."""
    return list(_PROFILES.values())
