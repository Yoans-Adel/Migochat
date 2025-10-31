"""
Database Context Module
Context managers for safe database session handling
"""
import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.engine import get_session

logger = logging.getLogger(__name__)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic cleanup
    
    Usage:
        with get_db_session() as db:
            user = db.query(User).first()
            # Session is automatically closed
    
    Yields:
        Session: SQLAlchemy session
    """
    session = None
    
    try:
        session = get_session()
        yield session
        
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        logger.error(f"Database error in session: {e}", exc_info=True)
        raise
        
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"Unexpected error in session: {e}", exc_info=True)
        raise
        
    finally:
        if session:
            session.close()


@contextmanager
def get_db_session_with_commit() -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic commit
    
    Usage:
        with get_db_session_with_commit() as db:
            user = User(psid="123", first_name="John")
            db.add(user)
            # Automatically commits and closes
    
    Yields:
        Session: SQLAlchemy session
    """
    session = None
    
    try:
        session = get_session()
        yield session
        session.commit()
        
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        logger.error(f"Database error, rolling back: {e}", exc_info=True)
        raise
        
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"Unexpected error, rolling back: {e}", exc_info=True)
        raise
        
    finally:
        if session:
            session.close()


class DatabaseSessionManager:
    """Enhanced database session manager with retry logic"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_session(self, auto_commit: bool = False):
        """
        Get database session with optional auto-commit
        
        Args:
            auto_commit: Whether to automatically commit changes
            
        Yields:
            Session: SQLAlchemy session
        """
        session = None
        
        try:
            session = get_session()
            yield session
            
            if auto_commit:
                session.commit()
                
        except SQLAlchemyError as e:
            if session:
                session.rollback()
            self.logger.error(f"Database error: {e}", exc_info=True)
            raise
            
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
            
        finally:
            if session:
                session.close()
    
    def execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute database operation with retry logic
        
        Args:
            operation: Callable that performs database operation
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of the operation
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with self.get_session() as session:
                    result = operation(session, *args, **kwargs)
                    session.commit()
                    return result
                    
            except SQLAlchemyError as e:
                last_error = e
                self.logger.warning(
                    f"Database operation failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                
                if attempt == self.max_retries - 1:
                    self.logger.error(f"All retry attempts failed: {e}", exc_info=True)
                    raise
                    
            except Exception as e:
                self.logger.error(f"Unexpected error in operation: {e}", exc_info=True)
                raise
        
        if last_error:
            raise last_error


# Global session manager instance
_session_manager = DatabaseSessionManager()


def get_safe_session(auto_commit: bool = False):
    """
    Get safe database session with error handling
    
    Args:
        auto_commit: Whether to automatically commit changes
        
    Returns:
        Context manager for database session
    """
    return _session_manager.get_session(auto_commit=auto_commit)


def execute_db_operation(operation, *args, **kwargs):
    """
    Execute database operation with retry logic
    
    Args:
        operation: Callable that performs database operation
        *args: Positional arguments for operation
        **kwargs: Keyword arguments for operation
        
    Returns:
        Result of the operation
    """
    return _session_manager.execute_with_retry(operation, *args, **kwargs)
