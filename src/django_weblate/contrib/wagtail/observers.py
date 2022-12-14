from wagtail.blocks.struct_block import StructValue
from wagtail.blocks.stream_block import StreamValue
from wagtail.blocks.list_block import ListValue


class BaseWagtailStreamObserver:
    def __init__(self, value):
        self.value = value
        self.buffer = []

    def feed(self, parent, item, **kwargs):
        # TODO: as an object
        self.buffer += [(parent, item, kwargs)]

    def pop(self, *items):
        return self.buffer.pop(0)

    def walk(self):
        self.feed(None, self.value)

        while self.buffer:
            parent, item, kwargs = self.pop()
            # Stream
            if isinstance(item, StreamValue):
                self.handle_stream_value(parent, item, **kwargs)
            elif isinstance(item, StreamValue.StreamChild):
                self.handle_stream_child(parent, item, **kwargs)
            # Struct
            elif isinstance(item, StructValue):
                self.handle_struct_value(parent, item, **kwargs)
            # Lists
            elif isinstance(item, ListValue):
                self.handle_list_value(parent, item, **kwargs)
            elif isinstance(item, ListValue.ListChild):
                self.handle_list_child(parent, item, **kwargs)
            # Scalar
            elif isinstance(item, str):
                self.handle_scalar_value(parent, item, **kwargs)

    def handle_stream_value(self, parent, value, **kwargs):
        for item in value:
            self.feed(value, item)

    def handle_stream_child(self, parent, value, **kwargs):
        self.feed(value, value.value)

    def handle_struct_value(self, parent, value, **kwargs):
        for name, item in value.items():
            self.feed(parent, item, name=name)

    def handle_list_value(self, parent, value, **kwargs):
        for item in value.bound_blocks:
            self.feed(value, item)

    def handle_list_child(self, parent, value, **kwargs):
        self.feed(value, value.value)

    def handle_scalar_value(self, parent, value, **kwargs):
        raise NotImplementedError()


class WagtailStreamRawDataObserver:
    def __init__(self, value):
        self.value = value
        self.buffer = []

    def feed(self, parent, item, **kwargs):
        self.buffer += [(parent, item, kwargs)]

    def pop(self, *items):
        return self.buffer.pop(0)

    def walk(self):
        self.feed(None, self.value)

        while self.buffer:
            parent, item, kwargs = self.pop()
            if isinstance(item, list):
                self.handle_list(parent, item, **kwargs)
            elif isinstance(item, dict) and "id" in item:
                self.handle_block(parent, item, **kwargs)
            else:
                self.handle_scalar(parent, item, **kwargs)

    def handle_list(self, parent, value, **kwargs):
        for item in value:
            self.feed(parent, item)

    def handle_block(self, parent, block, **kwargs):
        value = block.get("value")
        if isinstance(value, dict):
            for name, item in value.items():
                self.feed(block, item, name=name)
        elif isinstance(value, list):
            for item in value:
                self.feed(block, item)
        else:
            self.handle_scalar(block, value, **kwargs)

    def handle_scalar(self, parent, value, **kwargs):
        raise NotImplementedError()
