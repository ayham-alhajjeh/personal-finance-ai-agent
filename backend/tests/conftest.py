import pytest
import sys
from pathlib import Path

# Add the backend/app directory to the Python path
backend_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.database import Base, get_db
from models.user import UserDB
from utils.security import hash_password
from utils.jwt import create_access_token


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database"""
    user = UserDB(
        email="testuser@example.com",
        name="Test User",
        hashed_password=hash_password("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Generate a JWT token for the test user"""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def auth_headers(test_user_token):
    """Create authorization headers with JWT token"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def second_user(db_session):
    """Create a second test user for authorization tests"""
    user = UserDB(
        email="seconduser@example.com",
        name="Second User",
        hashed_password=hash_password("password456")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_user_token(second_user):
    """Generate a JWT token for the second test user"""
    return create_access_token(data={"sub": str(second_user.id)})


@pytest.fixture
def second_auth_headers(second_user_token):
    """Create authorization headers for second user"""
    return {"Authorization": f"Bearer {second_user_token}"}
