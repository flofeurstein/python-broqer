"""
>>> from broqer import Hub, Value, op
>>> hub = Hub()

The hub is handling with topics referencing to publishers or subjects:

>>> value1 = hub['value1']

Each following access will return the same object

>>> value1 == hub['value1']
True

It's possible to subscribe to a topic

>>> _d1 = hub['value1'] | op.sink(print, 'Output:')

At the moment this hub object is not assigned to a publisher

>>> hub['value1'].assigned
False

Checking if a topic already exists is done via ``in`` operator

>>> 'value1' in hub
True
>>> 'value2' in hub
False

It will raise an exception if .emit is used on an unassigned topic:

>>> hub['value1'].emit(1)
Traceback (most recent call last):
...
TypeError: No subject is assigned to this Topic

Assign a publisher to a hub topic:

>>> _ = op.Just(1) | hub.publish('value1')
Output: 1
>>> hub['value1'].assigned
True

Assigning to a hub topic without .publish will fail:

>>> _ = op.Just(1) | hub['value2']
Traceback (most recent call last):
...
TypeError: Topic is not callable (for use as operator). ...

>>> _d1.dispose()

Also assigning publisher first and then subscribing is possible:

>>> _ = Value(2) | hub.publish('value2')
>>> _d2 = hub['value2'] | op.sink(print, 'Output:')
Output: 2

>>> hub['value2'].emit(3)
Output: 3

>>> _d2.dispose()

It's not possible to assign a second publisher to a hub topic:

>>> _ = Value(0) | hub.publish('value2')
Traceback (most recent call last):
...
ValueError: Topic is already assigned

Meta data
---------

Another feature is defining meta data as dictionary to a hub topic:

>>> _ = Value(0) | hub.publish('value3', meta={'maximum':10})
>>> hub['value3'].meta
{'maximum': 10}

Wait for assignment
-------------------

It's also possible to wait for an assignment:

>>> import asyncio
>>> _f1 = asyncio.ensure_future(hub['value4'].wait_for_assignment(0.01))
>>> asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.02))
>>> _f1.exception()
TimeoutError()

>>> _f2 = asyncio.ensure_future(hub['value4'].wait_for_assignment())
>>> asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.02))
>>> _f2.done()
False

>>> _ = Value(0) | hub.publish('value4')
>>> asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.01))
>>> _f2.done()
True

When already assigned it will not wait at all:

>>> _f2 = asyncio.ensure_future(hub['value4'].wait_for_assignment())
>>> asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.01))
>>> _f2.done()
True
"""
import asyncio
from collections import defaultdict
from typing import Any, Callable, Optional

from broqer import Publisher, Subscriber, SubscriptionDisposable


class Topic(Publisher, Subscriber):
    def __init__(self):
        super().__init__()
        self._subject = None

    def subscribe(self, subscriber: 'Subscriber') -> SubscriptionDisposable:
        disposable = Publisher.subscribe(self, subscriber)
        if len(self._subscriptions) == 1 and self._subject is not None:
            # if this was the first subscription
            self._subject.subscribe(self)
        return disposable

    def unsubscribe(self, subscriber: 'Subscriber') -> None:
        Publisher.unsubscribe(self, subscriber)
        if not self._subscriptions and self._subject is not None:
            self._subject.unsubscribe(self)

    def emit(self, *args: Any, who: Optional[Publisher]=None) -> None:
        if self._subject is None:
            # method will be replaced by .__call__
            raise TypeError('No subject is assigned to this Topic')
        elif who == self._subject:
            self._emit(*args)
        elif who != self._subject:
            self._subject.emit(*args)

    def __call__(self, *args, **kwargs) -> None:
        raise TypeError('Topic is not callable (for use as operator).' +
                        ' Use "| hub.publish(topic, meta)" instead.')

    @property
    def assigned(self):
        return self._subject is not None

    async def wait_for_assignment(self, timeout=None):
        if self.assigned:
            return
        else:
            self._assignment_future = asyncio.get_event_loop().create_future()
            if timeout is None:
                await self._assignment_future
            else:
                await asyncio.wait_for(
                    asyncio.shield(self._assignment_future), timeout)

    @property
    def meta(self):
        return getattr(self, '_meta', None)


class Hub:
    def __init__(self):
        self._proxies = defaultdict(Topic)

    def __getitem__(self, topic: str) -> Topic:
        return self._proxies[topic]

    def __contains__(self, topic: str) -> bool:
        return topic in self._proxies

    def publish(self, topic: str, meta: Optional[dict]=None) \
            -> Callable[[Publisher], Publisher]:
        proxy = self[topic]

        def _build(publisher):
            # used for pipeline style assignment
            if proxy._subject is not None:
                raise ValueError('Topic is already assigned')
            else:
                proxy._subject = publisher

            if len(proxy._subscriptions):
                proxy._subject.subscribe(proxy)

            if meta:
                proxy._meta = meta

            if hasattr(proxy, '_assignment_future'):
                proxy._assignment_future.set_result(None)

            return proxy
        return _build