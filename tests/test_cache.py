from datetime import datetime, timedelta

import pytest

from app.utils.cache import CacheManager


@pytest.fixture
def cache_manager():
    cache = CacheManager()
    cache.clear()
    return cache


def test_set_and_get_cache(cache_manager):
    key = "test_key"
    value = {"data": "test_value"}

    assert cache_manager.set(key, value) is True
    assert cache_manager.get(key) == value


def test_get_non_existent_key(cache_manager):
    assert cache_manager.get("non_existent") is None


def test_cache_expiry(cache_manager):
    key = "expiry_test"
    value = "test_data"

    cache_manager.set(key, value, ttl=1)
    assert cache_manager.get(key) == value

    # Manually expire the cache entry
    cache_entry = cache_manager._memory_cache[key]
    cache_entry["expiry"] = datetime.utcnow() - timedelta(seconds=1)

    assert cache_manager.get(key) is None
    assert key not in cache_manager._memory_cache


def test_delete_cache(cache_manager):
    key = "delete_test"
    value = "test_data"

    cache_manager.set(key, value)
    assert cache_manager.get(key) == value

    assert cache_manager.delete(key) is True
    assert cache_manager.get(key) is None


def test_delete_non_existent_key(cache_manager):
    assert cache_manager.delete("non_existent") is False


def test_clear_cache(cache_manager):
    cache_manager.set("key1", "value1")
    cache_manager.set("key2", "value2")

    assert len(cache_manager._memory_cache) == 2

    assert cache_manager.clear() is True
    assert len(cache_manager._memory_cache) == 0


def test_cache_stats(cache_manager):
    cache_manager.set("key1", "value1")
    cache_manager.set("key2", "value2", ttl=1)

    # Manually expire one entry
    cache_entry = cache_manager._memory_cache["key2"]
    cache_entry["expiry"] = datetime.utcnow() - timedelta(seconds=1)

    stats = cache_manager.get_cache_stats()

    assert stats["total_entries"] == 2
    assert stats["active_entries"] == 1
    assert stats["expired_entries"] == 1
    assert stats["cache_ttl"] == 3600


def test_cache_with_different_data_types(cache_manager):
    test_cases = [
        ("string", "test_string"),
        ("integer", 12345),
        ("float", 123.45),
        ("list", [1, 2, 3, "test"]),
        ("dict", {"key": "value", "number": 42}),
        ("boolean", True),
    ]

    for key, value in test_cases:
        cache_manager.set(key, value)
        assert cache_manager.get(key) == value
