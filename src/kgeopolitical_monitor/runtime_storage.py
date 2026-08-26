"""Project-local runtime storage boundary for M5 operational execution."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeStoragePolicy:
    project_root: Path
    data_directory_name: str = "data"
    default_database_name: str = "kgeopolitical_monitor.db"

    @property
    def data_root(self) -> Path:
        return (self.project_root / self.data_directory_name).resolve()

    def resolve_database(self, database_path: str | Path | None = None) -> Path:
        root = self.project_root.resolve()
        data_root = self.data_root

        if database_path is None:
            candidate = data_root / self.default_database_name
        else:
            raw = Path(database_path)
            candidate = raw if raw.is_absolute() else root / raw
            candidate = candidate.resolve()

        try:
            candidate.relative_to(data_root)
        except ValueError as exc:
            raise ValueError(
                "M5 runtime database must remain inside the project-local data directory"
            ) from exc

        if candidate == data_root:
            raise ValueError("M5 runtime database path must identify a file")

        return candidate
