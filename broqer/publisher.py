""" Implementing Publisher """
from typing import TYPE_CHECKING, Union, TypeVar, Type, Tuple, Callable, \
                   Optional, Generic

from .types import NONE
from .disposable import SubscriptionDisposable

if TYPE_CHECKING:
    from broqer.subscriber import Subscriber


class SubscriptionError(ValueError):
    """ Special exception raised when subscription is failing (subscriber
    already subscribed) or on unsubscribe when subscriber is not subscribed
    """


TInherit = TypeVar('TInherit')  # Type to inherited behavior from
TValue = TypeVar('TValue')  # Type of publisher state and emitted value
TValueNONE = Union[TValue, NONE]  # when type can be TValue or NONE
SubscriptionCBT = Callable[[bool], None]


class Publisher(Generic[TInherit]):
    """ In broqer a subscriber can subscribe to a publisher. After subscription
    the subscriber is notified about emitted values from the publisher (
    starting with the current state). In other frameworks
    *publisher*/*subscriber* are referenced as *observable*/*observer*.

    broqer.NONE is used as default initialisation. .get() will always
    return the internal state (even when it's broqer.NONE). .subscribe() will
    emit the actual state to the new subscriber only if it is something else
    than broqer.NONE .

    To receive information use following methods to interact with Publisher:

    - ``.subscribe(subscriber)`` to subscribe for events on this publisher
    - ``.unsubscribe(subscriber)`` to unsubscribe
    - ``.get()`` to get the current state

    When implementing a Publisher use the following methods:

    - ``.notify(value)`` calls .emit(value) on all subscribers

    :param init: the initial state.

    :ivar _state: state of the publisher
    :ivar _inherited_type: type class for method lookup
    :ivar _subscriptions: holding a list of subscribers
    :ivar _on_subscription_cb: callback with boolean as argument, telling
                                if at least one subscription exists
    :ivar _dependencies: list with publishers this publisher is (directly or
                         indirectly) dependent on.
    """
    def __init__(self, init: TValueNONE = NONE):
        self._state = init
        self._inherited_type = None  # type: Optional[Type[TInherit]]
        self._subscriptions = list()  # type: List[Subscriber]
        self._on_subscription_cb = None  # type: Optional[SubscriptionCBT]
        self._dependencies = ()  # type: Tuple[Publisher, ...]

    def subscribe(self, subscriber: 'Subscriber',
                  prepend: bool = False) -> SubscriptionDisposable:
        """ Subscribing the given subscriber.

        :param subscriber: subscriber to add
        :param prepend: For internal use - usually the subscribers will be
            added at the end of a list. When prepend is True, it will be added
            in front of the list. This will habe an effect in the order the
            subscribers are called.
        :raises SubscriptionError: if subscriber already subscribed
        """

        # `subscriber in self._subscriptions` is not working because
        # tuple.__contains__ is using __eq__ which is overwritten and returns
        # a new publisher - not helpful here
        if any(subscriber is s for s in self._subscriptions):
            raise SubscriptionError('Subscriber already registered')

        if not self._subscriptions and self._on_subscription_cb:
            self._on_subscription_cb(True)

        if prepend:
            self._subscriptions.insert(0, subscriber)
        else:
            self._subscriptions.append(subscriber)

        disposable = SubscriptionDisposable(self, subscriber)

        if self._state is not NONE:
            subscriber.emit(self._state, who=self)

        return disposable

    def unsubscribe(self, subscriber: 'Subscriber') -> None:
        """ Unsubscribe the given subscriber

        :param subscriber: subscriber to unsubscribe
        :raises SubscriptionError: if subscriber is not subscribed (anymore)
        """
        # here is a special implementation which is replacing the more
        # obvious one: self._subscriptions.remove(subscriber) - this will not
        # work because list.remove(x) is doing comparison for equality.
        # Applied to publishers this will return another publisher instead of
        # a boolean result
        for i, _s in enumerate(self._subscriptions):
            if _s is subscriber:
                self._subscriptions.pop(i)

                if not self._subscriptions and self._on_subscription_cb:
                    self._on_subscription_cb(False)

                return

        raise SubscriptionError('Subscriber is not registered')

    def get(self) -> TValueNONE:
        """ Return the state of the publisher. """
        return self._state

    def notify(self, value: TValue) -> None:
        """ Calling .emit(value) on all subscribers and store state.

        :param value: value to be emitted to subscribers
        """
        self._state = value
        for s in self._subscriptions:
            s.emit(value, who=self)

    def reset_state(self, value: TValueNONE = NONE) -> None:
        """ Resets the state. Calling this method will not trigger an emit.

        :param value: Optional value to set the internal state
        """
        self._state = value

    @property
    def subscriptions(self) -> Tuple['Subscriber', ...]:
        """ Property returning a tuple with all current subscribers """
        return tuple(self._subscriptions)

    def register_on_subscription_callback(self, cb: SubscriptionCBT) -> None:
        """ This callback will be called, when the subscriptions are changing.
        When a subscription is done and no subscription was present the
        callback is called with True as argument. When after unsubscribe no
        subscription is left, it will be called with False.

        :param cb: callback(subscription: bool) to be called.
        :raises ValueError: when a callback is already registrered
        """
        if self._on_subscription_cb is not None:
            raise ValueError('A callback is already registered')

        self._on_subscription_cb = cb

    def wait(self, timeout: float, omit_subscription=True, loop=None):
        """ Returns a asyncio.Future which will be done on first change of this
        publisher.

        :param timeout: timeout in seconds. Use None for infinite waiting
        :param omit_subscription: if True the first emit (which can be on the
            subscription) will be ignored.
        :param loop: asyncio loop to be used
        :returns: a future returning the emitted value
        """
        from broqer.op import OnEmitFuture  # due circular dependency

        if self._state is NONE:
            omit_subscription = False

        return OnEmitFuture(self, timeout, omit_subscription, loop)

    def __bool__(self):
        """ A new Publisher is the result of a comparision between a publisher
        and something else (may also be a second publisher). This result should
        never be used in a boolean sense (e.g. in `if p1 == p2:`). To prevent
        this __bool__ is overwritten to raise a ValueError.
        """
        raise ValueError('Evaluation of comparison of publishers is not '
                         'supported')

    def inherit_type(self, type_cls: Type[TInherit]) \
            -> Union[TInherit, 'Publisher']:
        """ Enables the usage of method and attribute overloading for this
        publisher.
        """
        self._inherited_type = type_cls
        return self

    @property
    def inherited_type(self) -> Optional[Type[TInherit]]:
        """ Property inherited_type returns used type class (or None) """
        return self._inherited_type

    @property
    def dependencies(self) -> Tuple['Publisher', ...]:
        """ Returning a list of publishers this publisher is dependent on. """
        return self._dependencies

    def add_dependencies(self, *publishers: 'Publisher') -> None:
        self._dependencies = self._dependencies + publishers
