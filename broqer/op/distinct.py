"""
Only emit values which changed regarding to the cached state.

Usage:

>>> from broqer import Subject, op
>>> s = Subject()

>>> distinct_publisher = s | op.distinct()
>>> _disposable = distinct_publisher | op.sink(print)

>>> s.emit(1)
1
>>> s.emit(2)
2
>>> s.emit(2)
>>> _disposable.dispose()

Also working with multiple arguments in emit:

>>> distinct_publisher = s | op.distinct(0, 0)
>>> distinct_publisher | op.sink(print)
0 0
<...>
>>> s.emit(0, 0)
>>> s.emit(0, 1)
0 1
"""

from typing import Any

from broqer import Publisher, Subscriber, SubscriptionDisposable

from ._operator import Operator, build_operator


class Distinct(Operator):
    def __init__(self, publisher: Publisher, *init: Any) -> None:
        Operator.__init__(self, publisher)
        if not init:
            self._state = None
        else:
            self._state = init

    def subscribe(self, subscriber: Subscriber) -> SubscriptionDisposable:
        state = self._state  # replace self._state temporary with None
        self._state = None
        disposable = Operator.subscribe(self, subscriber)
        if self._state is None and state is not None:
            # if subscriber was not emitting on subscription
            self._state = state  # set self._state back
            subscriber.emit(*self._state, who=self)  # and emit actual cache
        return disposable

    def emit(self, *args: Any, who: Publisher) -> None:
        assert who == self._publisher, 'emit from non assigned publisher'
        assert len(args) >= 1, 'need at least one argument for distinct'
        if args != self._state:
            self._state = args
            self.notify(*args)


distinct = build_operator(Distinct)  # pylint: disable=invalid-name
