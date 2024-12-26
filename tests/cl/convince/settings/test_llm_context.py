# Copyright (C) 2023-present The Project Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from random import Random
from cl.runtime.context.base_context import BaseContext
from cl.runtime.context.context import Context
from cl.runtime.parsers.locale_key import LocaleKey
from cl.convince.context.llm_context import LlmContext

TASK_COUNT = 3
MAX_SLEEP_DURATION = 0.2


def _verify_no_current_context(*, where_str: str):
    """Check for current context, raise an error if it exists when is_inner is False."""
    try:
        current_context = LlmContext.current()
        # If LlmContext.current() succeeds, it was leaked from outside the environment, raise an error
        raise RuntimeError(f"Context.LlmContext() is leaked from outside the asynchronous environment {where_str}.")
    except RuntimeError:
        # Raised as expected, continue
        pass


def _sleep(*, task_index: int, rnd: Random, max_sleep_duration: float):
    """Sleep for a random interval, reducing the interval for higher task index."""
    duration = rnd.uniform(0, max_sleep_duration) * (TASK_COUNT - task_index) / TASK_COUNT
    time.sleep(duration)


async def _sleep_async(*, task_index: int, rnd: Random, max_sleep_duration: float):
    """Sleep for a random interval, reducing the interval for higher task index."""
    duration = rnd.uniform(0, max_sleep_duration) * (TASK_COUNT - task_index) / TASK_COUNT
    await asyncio.sleep(duration)


def _perform_testing(
    *,
    task_index: int,
    rnd: Random,
    max_sleep_duration: float = MAX_SLEEP_DURATION,
):
    """Use for testing in-process or in multiple threads."""

    # Sleep before entering the task
    _sleep(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)

    # Task label
    task_label = f"async task {task_index}"

    # Verify that there is no current context
    _verify_no_current_context(where_str=f"before {task_label}")
    _sleep(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)

    llm_context_1 = LlmContext(locale=LocaleKey(locale_id="en-US"))
    with llm_context_1:
        _sleep(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)
        assert LlmContext.current() is llm_context_1
        llm_context_2 = LlmContext(locale=LocaleKey(locale_id="en-GB"))
        with llm_context_2:
            _sleep(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)
            assert LlmContext.current() is llm_context_2
        assert LlmContext.current() is llm_context_1

    # Verify that there is no current context
    _verify_no_current_context(where_str=f"after {task_label}")


async def _perform_testing_async(
    *,
    task_index: int,
    rnd: Random,
    is_inner: bool = False,
    max_sleep_duration: float = MAX_SLEEP_DURATION,
):
    """Use for testing in async loop."""

    # Sleep before entering the task
    await _sleep_async(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)

    # Task label
    task_label = f"async task {task_index}"

    # Verify that there is no current context
    _verify_no_current_context(where_str=f"before {task_label}")
    await _sleep_async(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)

    llm_context_1 = LlmContext(locale=LocaleKey(locale_id="en-US"))
    with llm_context_1:
        await _sleep_async(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)
        assert LlmContext.current() is llm_context_1
        llm_context_2 = LlmContext(locale=LocaleKey(locale_id="en-GB"))
        with llm_context_2:
            await _sleep_async(task_index=task_index, rnd=rnd, max_sleep_duration=max_sleep_duration)
            assert LlmContext.current() is llm_context_2
        assert LlmContext.current() is llm_context_1

    # Verify that there is no current context
    _verify_no_current_context(where_str=f"after {task_label}")


async def _gather(rnd: Random):
    """Gather async functions."""
    tasks = [_perform_testing_async(task_index=i, rnd=rnd) for i in range(TASK_COUNT)]
    await asyncio.gather(*tasks)


def test_error_handling():
    """Test error handling in specifying extensions."""

    llm_context_1 = LlmContext(locale=LocaleKey(locale_id="en-US"))
    llm_context_2 = LlmContext(locale=LocaleKey(locale_id="en-GB"))

    # Two with on the same object
    with pytest.raises(RuntimeError):
        with llm_context_1:
            with llm_context_1:
                pass

    # Raise if modified other by exiting from 'with'
    with pytest.raises(RuntimeError):
        with llm_context_1:
            llm_context_1.__exit__(None, None, None)

    # Raise if exiting another instance
    with pytest.raises(RuntimeError):
        with llm_context_1:
            llm_context_2.__exit__(None, None, None)


def test_in_process():
    """Test in different threads."""

    # Create a local random instance with seed
    rnd = Random(0)

    # Run sequentially in-process
    [_perform_testing(task_index=task_index, rnd=rnd, max_sleep_duration=0) for task_index in range(TASK_COUNT)]


def test_in_threads():
    """Test in different threads."""

    # Create a local random instance with seed
    rnd = Random(0)

    # Run in parallel threads
    with ThreadPoolExecutor(max_workers=TASK_COUNT) as executor:
        futures = [
            executor.submit(_perform_testing, **{"task_index": task_index, "rnd": rnd})
            for task_index in range(TASK_COUNT)
        ]
    for future in futures:
        future.result()


def test_in_async_loop():
    """Test in different async environments."""

    # Save previous state of context stack before async method execution
    contextvar_token = BaseContext.clear_contextvar()
    try:
        # Create a local random instance with seed
        rnd = Random(0)

        # Run using cooperative multitasking (asyncio)
        asyncio.run(_gather(rnd))
    finally:
        # Restore previous state of context stack after async method execution even if an exception occurred
        BaseContext.restore_contextvar(contextvar_token)


if __name__ == "__main__":
    pytest.main([__file__])
