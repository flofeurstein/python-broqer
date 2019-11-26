import pytest
from unittest import mock

from broqer.op import CombineLatest, Sink, build_combine_latest
from broqer import Publisher, NONE

from .helper import check_multi_operator, Collector

@pytest.mark.parametrize('kwargs, input_vector, output_vector', [
    ({}, ((1,2), (NONE,3), (2,NONE), (2,3)), ((1,2),(1,3),(2,3),NONE)),
    ({}, ((1,), (2,), (2,), (3,)), (( (1,), (2,), NONE, (3,)))),
    ({}, ((1,NONE,NONE,NONE), (NONE,2,NONE,NONE), (NONE,3,NONE,NONE), (NONE,NONE,4,5)), ((NONE,NONE,NONE,(1,3,4,5)))),
    ({'map_':lambda a,b:a+b}, ((1,1), (NONE, 2), (1, NONE), (NONE, -5)), (2, 3, NONE, -4)),
    ({'map_':lambda a,b:a>b}, ((1,1), (NONE, 2), (1, NONE), (NONE, -5)), (False, NONE, NONE, True)),
    ({'map_':lambda a,b:NONE if a>b else a-b}, ((0, 0), (NONE, 1), (1, NONE), (NONE, 0), (0, NONE)), (0, -1, 0, NONE, 0)),
])
def test_with_publisher(kwargs, input_vector, output_vector):
    check_multi_operator(CombineLatest, kwargs, input_vector, output_vector, has_state=None)

def test_emit_on():
    source = Publisher()
    source2 = Publisher()
    dut = CombineLatest(source, source2, emit_on=source2)
    dut2 = CombineLatest(source, source2, emit_on=(source, source2))
    dut3 = CombineLatest(source, source2, emit_on=source, map_=lambda a,b:a+b)

    collector = Collector()
    collector2 = Collector()
    collector3 = Collector()
    dut.subscribe(collector)
    dut2.subscribe(collector2)
    dut3.subscribe(collector3)

    source2.notify(1)
    source.notify(2)
    source2.notify(0)
    source.notify(1)
    assert collector.result_vector == ((2,0),)
    assert collector2.result_vector == ((2,1), (2,0), (1,0))
    assert collector3.result_vector == (3, 1)


def test_no_publishers():
    dut = CombineLatest()

    collector = Collector()
    dut.subscribe(collector)

    assert collector.result_vector == ((),)
