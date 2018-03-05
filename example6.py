from broqer.stream import Stream
import asyncio
from functools import partial

async def delay_coro(value):
    await asyncio.sleep(1)
    return value

value=Stream()
value.sink(print)
value.map_async(delay_coro).sink(lambda v:print('Delayed:',v))

async def main():
    for i in range(10):
        value.emit(i)
        await asyncio.sleep(0.3)

loop=asyncio.get_event_loop()
loop.run_until_complete(main())