"""Repository interfaces for domain persistence."""


class SourceRepository:
    def save(self, source):
        raise NotImplementedError

    def get(self, source_id):
        raise NotImplementedError


class RawItemRepository:
    def save(self, raw_item):
        raise NotImplementedError

    def get(self, raw_item_id):
        raise NotImplementedError


class EventRepository:
    def save(self, event):
        raise NotImplementedError

    def get(self, event_id):
        raise NotImplementedError
