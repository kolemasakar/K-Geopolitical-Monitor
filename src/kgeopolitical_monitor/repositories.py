"""Repository interfaces for domain persistence."""

class EventRepository:
    def save(self, event):
        raise NotImplementedError

    def get(self, event_id):
        raise NotImplementedError
