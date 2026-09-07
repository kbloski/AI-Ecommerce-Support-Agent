from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def unit_of_work(db: Session):
    """Commits the session once at the end of the block, rolling back on any error.

    Repositories used inside the block must `flush()` instead of `commit()` so
    partial writes never become visible if a later step in the same business
    operation fails.
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
