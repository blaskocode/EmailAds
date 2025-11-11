"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from app.main import app
from app.database import db
import os
import tempfile
import shutil


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    """Create a temporary test database"""
    # Create temporary database file
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_campaigns.db")
    
    # Override database path for testing
    original_db_path = os.environ.get("DATABASE_URL", "")
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"
    
    # Initialize test database
    await db.init_db()
    
    yield db
    
    # Cleanup
    await db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Restore original database path
    if original_db_path:
        os.environ["DATABASE_URL"] = original_db_path
    elif "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]


@pytest.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_openai_client(monkeypatch):
    """Mock OpenAI client for testing"""
    class MockOpenAIClient:
        def __init__(self, *args, **kwargs):
            pass
        
        class Chat:
            class Completions:
                @staticmethod
                async def create(*args, **kwargs):
                    return type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {
                                'content': '{"subject_variations": ["Test Subject 1", "Test Subject 2", "Test Subject 3"], "preview_text": "Test preview", "body_copy": "Test body", "cta_text": "Click Here"}'
                            })()
                        })()]
                    })()
        
        class Images:
            class Analyze:
                @staticmethod
                async def create(*args, **kwargs):
                    return type('obj', (object,), {
                        'choices': [type('obj', (object,), {
                            'message': type('obj', (object,), {
                                'content': 'This is a test image showing a product.'
                            })()
                        })()]
                    })()
    
    monkeypatch.setattr("app.services.ai_service.get_openai_client", lambda: MockOpenAIClient())
    return MockOpenAIClient


@pytest.fixture
def mock_s3_service(monkeypatch):
    """Mock S3 service for testing"""
    class MockS3Service:
        async def upload_file(self, file_content, s3_key):
            return f"https://s3.amazonaws.com/test-bucket/{s3_key}"
        
        async def test_connection(self):
            return True
        
        async def get_signed_url(self, s3_key, expiration=3600):
            return f"https://s3.amazonaws.com/test-bucket/{s3_key}?signature=test"
    
    return MockS3Service()

