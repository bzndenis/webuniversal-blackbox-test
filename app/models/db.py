"""Database models using SQLModel."""

from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
import json
import os


class TestRun(SQLModel, table=True):
    """Test run record."""
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True, unique=True)
    base_url: str
    status: str = "pending"  # pending, running, completed, failed
    total_pages: int = 0
    passed: int = 0
    failed: int = 0
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    artifacts_path: Optional[str] = None
    config_json: Optional[str] = None  # JSON string of configuration
    

class PageTest(SQLModel, table=True):
    """Individual page test result."""
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(foreign_key="testrun.run_id", index=True)
    url: str
    status: str  # PASS, FAIL, ERROR, etc.
    http_status: Optional[int] = None
    load_ms: Optional[int] = None
    console_errors_count: int = 0
    network_failures_count: int = 0
    assertions_passed: int = 0
    assertions_total: int = 0
    forms_found: int = 0
    screenshot_path: Optional[str] = None
    result_json: Optional[str] = None  # Full result as JSON
    timestamp: datetime = Field(default_factory=datetime.now)


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_runs.db")
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get database session."""
    return Session(engine)


def create_test_run(
    run_id: str,
    base_url: str,
    config: dict = None
) -> TestRun:
    """
    Create a new test run record.
    
    Args:
        run_id: Unique run identifier
        base_url: Base URL being tested
        config: Optional configuration dictionary
        
    Returns:
        Created TestRun object
    """
    test_run = TestRun(
        run_id=run_id,
        base_url=base_url,
        status="pending",
        config_json=json.dumps(config) if config else None
    )
    
    with get_session() as session:
        session.add(test_run)
        session.commit()
        session.refresh(test_run)
    
    return test_run


def update_test_run(
    run_id: str,
    **kwargs
) -> Optional[TestRun]:
    """
    Update test run record.
    
    Args:
        run_id: Run identifier
        **kwargs: Fields to update
        
    Returns:
        Updated TestRun or None if not found
    """
    with get_session() as session:
        statement = select(TestRun).where(TestRun.run_id == run_id)
        test_run = session.exec(statement).first()
        
        if test_run:
            for key, value in kwargs.items():
                setattr(test_run, key, value)
            session.add(test_run)
            session.commit()
            session.refresh(test_run)
        
        return test_run


def create_page_test(
    run_id: str,
    url: str,
    result: dict
) -> PageTest:
    """
    Create page test record.
    
    Args:
        run_id: Associated run ID
        url: Page URL
        result: Test result dictionary
        
    Returns:
        Created PageTest object
    """
    assertions = result.get('assertions', [])
    assertions_passed = sum(1 for a in assertions if a.get('pass'))
    
    page_test = PageTest(
        run_id=run_id,
        url=url,
        status=result.get('status', 'UNKNOWN'),
        http_status=result.get('http_status'),
        load_ms=result.get('load_ms'),
        console_errors_count=len(result.get('console_errors', [])),
        network_failures_count=len(result.get('network_failures', [])),
        assertions_passed=assertions_passed,
        assertions_total=len(assertions),
        forms_found=result.get('forms_found', 0),
        screenshot_path=result.get('screenshot'),
        result_json=json.dumps(result)
    )
    
    with get_session() as session:
        session.add(page_test)
        session.commit()
        session.refresh(page_test)
    
    return page_test


def get_test_run(run_id: str) -> Optional[TestRun]:
    """Get test run by ID."""
    with get_session() as session:
        statement = select(TestRun).where(TestRun.run_id == run_id)
        return session.exec(statement).first()


def get_recent_runs(limit: int = 10) -> List[TestRun]:
    """Get recent test runs."""
    with get_session() as session:
        statement = select(TestRun).order_by(TestRun.start_time.desc()).limit(limit)
        return list(session.exec(statement))


def get_page_tests(run_id: str) -> List[PageTest]:
    """Get all page tests for a run."""
    with get_session() as session:
        statement = select(PageTest).where(PageTest.run_id == run_id)
        return list(session.exec(statement))

