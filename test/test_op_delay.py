import pytest

from broqer.op import Delay

from .helper import check_async_operator_coro, NONE

@pytest.mark.parametrize('duration, input_vector, output_vector', [
    # repeated False followed by repeated True
    (0.1,
     ((0, False), (0.05, False), (0.10, False), (0.15, True), (0.2, True), (0.25, True)),
     ((0.1, False), (0.15, False), (0.20, False), (0.25, True), (0.3, True), (0.35, True))),

    # short glitches
    (0.1,
     ((0, False), (0.2, True), (0.25, False), (0.4, True), (0.6, False), (0.65, True)),
     ((0.1, False), (0.3, True), (0.35, False), (0.5, True), (0.7, False), (0.75, True))),

    # short glitches with 0 delay
    (0,
     ((0, False), (0.2, True), (0.25, False), (0.4, True), (0.6, False), (0.65, True)),
     ((0.001, False), (0.2, True), (0.25, False), (0.4, True), (0.6, False), (0.65, True))),
     # ^-- have to fool check_async_operator_coro which is checking for 0 as really immediate

])
@pytest.mark.asyncio
async def test_with_publisher(duration, input_vector, output_vector, event_loop):
    await check_async_operator_coro(Delay, (duration,), {}, input_vector, output_vector, loop=event_loop)