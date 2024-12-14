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
import random
import time
from concurrent.futures import ThreadPoolExecutor
import asyncio
from cl.convince.context.llm_context import LlmContext
from cl.convince.llms.llm_key import LlmKey
from cl.runtime.context.testing_context import TestingContext
from cl.runtime.parsers.locale_key import LocaleKey
from cl.convince.settings.llm_settings import LlmSettings

# Create a local random instance with the seed
_RANDOM = random.Random(0)

def _sleep():
    """Sleep for a random interval from 0 to 1 sec."""
    duration = _RANDOM.uniform(0, 1)
    time.sleep(duration)

async def _sleep_async():
    """Sleep for a random interval from 0 to 1 sec."""
    duration = _RANDOM.uniform(0, 1)
    await asyncio.sleep(duration)

def _perform_testing():
    """Use for testing in-process or in multiple threads."""

    with TestingContext():

        # With clause, no fields set
        llm_settings = LlmSettings.instance()
        with LlmContext(is_root=True):
            # Sleep between entering 'with' clause and calling 'current'
            _sleep()
            llm_context = LlmContext.current()
            assert llm_context.locale.locale_id == llm_settings.locale
            assert llm_context.full_llm.llm_id == llm_settings.full
            assert llm_context.mini_llm.llm_id == llm_settings.mini

        # With clause, all fields set
        locale_param = LocaleKey(locale_id='en-US')
        full_llm_param = LlmKey(llm_id='full_llm')
        mini_llm_param = LlmKey(llm_id='mini_llm')
        with LlmContext(is_root=True, locale=locale_param, full_llm=full_llm_param, mini_llm=mini_llm_param):
            # Sleep between entering 'with' clause and calling 'current'
            _sleep()
            llm_context = LlmContext.current()
            assert llm_context.locale is locale_param
            assert llm_context.full_llm is full_llm_param
            assert llm_context.mini_llm is mini_llm_param

        # Call 'current' method outside with clause
        _sleep()
        with pytest.raises(RuntimeError):
            LlmContext.current()

        # With clause without setting is_root=True
        _sleep()
        with pytest.raises(RuntimeError):
            with LlmContext():
                pass

async def _perform_testing_async():
    """Use for testing in async loop."""

    with TestingContext():

        # With clause, no fields set
        llm_settings = LlmSettings.instance()
        with LlmContext(is_root=True):
            # Sleep between entering 'with' clause and calling 'current'
            await _sleep_async()
            llm_context = LlmContext.current()
            assert llm_context.locale.locale_id == llm_settings.locale
            assert llm_context.full_llm.llm_id == llm_settings.full
            assert llm_context.mini_llm.llm_id == llm_settings.mini

        # With clause, all fields set
        locale_param = LocaleKey(locale_id='en-US')
        full_llm_param = LlmKey(llm_id='full_llm')
        mini_llm_param = LlmKey(llm_id='mini_llm')
        with LlmContext(is_root=True, locale=locale_param, full_llm=full_llm_param, mini_llm=mini_llm_param):
            # Sleep between entering 'with' clause and calling 'current'
            await _sleep_async()
            llm_context = LlmContext.current()
            assert llm_context.locale is locale_param
            assert llm_context.full_llm is full_llm_param
            assert llm_context.mini_llm is mini_llm_param

        # Call 'current' method outside with clause
        await _sleep_async()
        with pytest.raises(RuntimeError):
            LlmContext.current()

        # With clause without setting is_root=True
        await _sleep_async()
        with pytest.raises(RuntimeError):
            with LlmContext():
                pass

async def _gather():
    """Gather async functions."""
    await asyncio.gather(
        _perform_testing_async(),
        _perform_testing_async(),
        _perform_testing_async(),
        _perform_testing_async(),
        _perform_testing_async()
    )

def test_in_process():
    """Test in different threads."""

    # Perform testing in process
    _perform_testing()

def test_in_threads():
    """Test in different threads."""
    thread_count = 5
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(_perform_testing) for _ in range(thread_count)]
    for future in futures:
        future.result()

def test_in_async_loop():
    """Test in different async environments."""
    asyncio.run(_gather())


if __name__ == "__main__":
    pytest.main([__file__])
