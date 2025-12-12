"""Tests to verify async safety of dynaconf with contextvars."""

import asyncio

import pytest

from dynaconf import Dynaconf


def test_contextvars_sync_isolation():
    """Test that evaluation stacks are isolated in sync/threaded contexts."""
    settings1 = Dynaconf()
    settings2 = Dynaconf()

    settings1.set("A", "@format {this.B}")
    settings1.set("B", "value1")

    settings2.set("A", "@format {this.B}")
    settings2.set("B", "value2")

    # Both should evaluate independently
    assert settings1.A == "value1"
    assert settings2.A == "value2"


@pytest.mark.asyncio
async def test_contextvars_async_isolation():
    """Test that evaluation stacks are isolated in async contexts."""

    async def task1():
        settings = Dynaconf()
        settings.set("VALUE", "@format Task1-{this.ID}")
        settings.set("ID", "1")
        # Simulate async work
        await asyncio.sleep(0.01)
        result = settings.VALUE
        assert result == "Task1-1", f"Expected 'Task1-1', got '{result}'"
        return result

    async def task2():
        settings = Dynaconf()
        settings.set("VALUE", "@format Task2-{this.ID}")
        settings.set("ID", "2")
        # Simulate async work
        await asyncio.sleep(0.01)
        result = settings.VALUE
        assert result == "Task2-2", f"Expected 'Task2-2', got '{result}'"
        return result

    # Run tasks concurrently - they should not interfere
    results = await asyncio.gather(task1(), task2())
    assert results[0] == "Task1-1"
    assert results[1] == "Task2-2"


@pytest.mark.asyncio
async def test_contextvars_async_circular_detection():
    """Test that circular reference detection works in async contexts."""

    async def task_with_circular_ref():
        settings = Dynaconf()
        settings.set("A", "@format {this.B}")
        settings.set("B", "@format {this.A}")

        # Should raise circular reference error
        with pytest.raises(Exception, match="Circular reference"):
            _ = settings.A

    # Run the task
    await task_with_circular_ref()


@pytest.mark.asyncio
async def test_contextvars_async_no_state_leakage():
    """Test that async tasks don't leak state between each other."""
    results = []

    async def task(task_id):
        settings = Dynaconf()
        settings.set("NESTED", "@format {this.LEVEL1}")
        settings.set("LEVEL1", f"@format Task{task_id}-{{this.LEVEL2}}")
        settings.set("LEVEL2", f"Value{task_id}")

        # Yield to allow interleaving
        await asyncio.sleep(0.001)

        result = settings.NESTED
        results.append((task_id, result))
        return result

    # Run 10 tasks concurrently
    await asyncio.gather(*[task(i) for i in range(10)])

    # Verify each task got its own value
    for task_id, result in results:
        expected = f"Task{task_id}-Value{task_id}"
        assert result == expected, (
            f"Task {task_id}: expected '{expected}', got '{result}'"
        )


def test_threaded_isolation():
    """Test that evaluation stacks are isolated in threaded contexts."""
    import threading

    results = {}

    def thread_task(thread_id):
        settings = Dynaconf()
        settings.set("VALUE", "@format Thread{this.ID}")
        settings.set("ID", str(thread_id))
        result = settings.VALUE
        results[thread_id] = result

    threads = [
        threading.Thread(target=thread_task, args=(i,)) for i in range(5)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # Verify each thread got its own value
    for thread_id, result in results.items():
        expected = f"Thread{thread_id}"
        assert result == expected, (
            f"Thread {thread_id}: expected '{expected}', got '{result}'"
        )
