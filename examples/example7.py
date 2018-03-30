from broqer.server import buildBroqerProtocol
from broqer.hub import Hub
from broqer.stream import Stream
from broqer import op
import asyncio

hub=Hub()

hub['msg']|op.sink(print)
Stream().setup(1.23)|op.sample(1)|hub['voltage']

loop=asyncio.get_event_loop()
server=loop.create_server(buildBroqerProtocol(hub), '127.0.0.1', 8888)
loop.run_until_complete(server)
loop.run_forever()