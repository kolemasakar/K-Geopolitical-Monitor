# SQLite repository implementation

from .repositories import SourceRepository, EventRepository, RawItemRepository

class SQLiteSourceRepository(SourceRepository):
    pass

class SQLiteRawItemRepository(RawItemRepository):
    pass

class SQLiteEventRepository(EventRepository):
    pass
