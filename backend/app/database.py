"""
Database connection and initialization
Uses aiosqlite for async SQLite operations
"""
import aiosqlite
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    def __init__(self):
        # Extract database path from DATABASE_URL
        # Format: sqlite:///./data/campaigns.db
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        self.db_path = Path(db_path)
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def connect(self):
        """Create database connection"""
        self.conn = await aiosqlite.connect(str(self.db_path))
        self.conn.row_factory = aiosqlite.Row
        logger.info(f"Connected to database: {self.db_path}")
        return self.conn
    
    async def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            await self.conn.close()
            logger.info("Database connection closed")
    
    async def init_db(self):
        """Initialize database schema and keep connection open"""
        if not hasattr(self, 'conn') or self.conn is None:
            await self.connect()
        await self.create_tables()
        logger.info("Database tables created successfully")
    
    async def create_tables(self):
        """Create database tables"""
        async with self.conn.cursor() as cursor:
            # Campaigns table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY,
                    campaign_name TEXT NOT NULL,
                    advertiser_name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    approved_at TEXT,
                    assets_s3_path TEXT,
                    html_s3_path TEXT,
                    proof_s3_path TEXT,
                    ai_processing_data TEXT,
                    updated_at TEXT
                )
            """)
            
            # Create indexes
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaigns_status 
                ON campaigns(status)
            """)
            
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaigns_created_at 
                ON campaigns(created_at)
            """)
            
            await self.conn.commit()
            logger.info("Database tables and indexes created")


# Global database instance
db = Database()


async def get_db():
    """
    Dependency for FastAPI to get database connection.
    Note: For now, we use a single connection. In production, consider connection pooling.
    """
    if not hasattr(db, 'conn') or db.conn is None:
        await db.connect()
    try:
        yield db.conn
    finally:
        # Don't close here - keep connection open for lifespan
        pass

