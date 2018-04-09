import asyncio
from typing import Any, List

from broqer import Publisher, Subscriber, SubscriptionDisposable


class Operator(Publisher, Subscriber):
  def __init__(self, publisher:Publisher):
    super().__init__()
    self._publisher=publisher

  def subscribe(self, subscriber:'Subscriber') -> SubscriptionDisposable:
    disposable=Publisher.subscribe(self, subscriber)
    if len(self._subscriptions)==1: # if this was the first subscription 
      self._publisher.subscribe(self)
    return disposable
  
  def unsubscribe(self, subscriber:'Subscriber') -> None:
    Publisher.unsubscribe(self, subscriber)
    if not self._subscriptions:
      self._publisher.unsubscribe(self)


class MultiOperator(Publisher, Subscriber):
  def __init__(self, *publishers:List[Publisher]):
    super().__init__()
    self._publishers=publishers

  def subscribe(self, subscriber:'Subscriber') -> SubscriptionDisposable:
    disposable=Publisher.subscribe(self, subscriber)
    if len(self._subscriptions)==1: # if this was the first subscription
      for _publisher in self._publishers: # subscribe to all dependent publishers
        _publisher.subscribe(self)
    return disposable
  
  def unsubscribe(self, subscriber:'Subscriber') -> None:
    Publisher.unsubscribe(self, subscriber)
    if not self._subscriptions:
      for _publisher in self._publishers:
        _publisher.unsubscribe(self)


def build_operator(operator_cls):
  def _op(*args, **kwargs):
    def _build(publisher):
      return operator_cls(publisher, *args, **kwargs)
    return _build
  return _op