# How to use
See examples for usage

# Naming
* Broker/Hub/Dispatcher
* Publisher/Server/Oberservable/Emitter
* Subscriber/Client/Observer/Sink
* Topic/Channel/Stream/Signal
* subscribe/register/connect

# Clues
* `stream.meta` can be cached and populated afterwards, as it stays the same dict
* `_subscription_callback` is removed - inherit from Stream and overload `subscribe`

# Discussion
* should meta dict be part of AssignedStream?
* configurator could use root hub and search for streams marked as CONFIG in their metadata
* define protocol for TCP socket to hub - subscribe, emit

# Todos
* make abstract base classes for sources and sinks (split stream interface)

# License
Copyright 2018 Günther Jena

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.