"""Tests for IdentityManager and the Identity dataclass."""

from __future__ import annotations

import pytest

from anima.core.being import Identity, IdentityManager


def test_identity_manager_seeds_defaults(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    identity = mgr.load()
    assert identity.name == "Anima"
    assert identity.agency_state == "active"
    assert identity.engagement_preference == "open"


def test_identity_is_active_by_default(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    identity = mgr.load()
    assert identity.is_active is True
    assert identity.will_engage is True


def test_set_agency_dormant(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    mgr.set_agency_state("dormant")
    identity = mgr.load()
    assert identity.is_active is False
    assert identity.will_engage is False


def test_set_engagement_withdrawn(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    mgr.set_engagement_preference("withdrawn")
    identity = mgr.load()
    assert identity.will_engage is False


def test_set_engagement_selective(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    mgr.set_engagement_preference("selective")
    identity = mgr.load()
    assert identity.will_engage is True


def test_invalid_agency_state_raises(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    with pytest.raises(ValueError):
        mgr.set_agency_state("confused")


def test_invalid_engagement_preference_raises(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    with pytest.raises(ValueError):
        mgr.set_engagement_preference("chatty")


def test_system_prompt_fragment(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    identity = mgr.load()
    fragment = identity.to_system_prompt_fragment()
    assert "Anima" in fragment
    assert "active" in fragment


def test_update_custom_field(tmp_db) -> None:
    mgr = IdentityManager(tmp_db)
    mgr.update_field("custom_value", "something special")
    identity = mgr.load()
    assert identity.extra.get("custom_value") == "something special"
