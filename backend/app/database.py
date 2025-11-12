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
        if hasattr(self, 'conn') and self.conn is not None:
            try:
                await self.conn.close()
                logger.info("Database connection closed")
            except ValueError as e:
                # Connection was already closed - this is fine during shutdown
                logger.debug(f"Database connection already closed: {e}")
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")
            finally:
                # Clear the connection reference
                self.conn = None
    
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
                    updated_at TEXT,
                    feedback TEXT
                )
            """)
            
            # Migrate existing tables to add feedback column if it doesn't exist
            await self.migrate_add_feedback_column(cursor)
            
            # Migrate existing tables to add scheduling columns if they don't exist
            await self.migrate_add_scheduling_columns(cursor)
            
            # Migrate existing tables to add review columns if they don't exist
            await self.migrate_add_review_columns(cursor)
            
            # Migrate existing tables to add performance columns if they don't exist
            await self.migrate_add_performance_columns(cursor)
            
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
    
    async def migrate_add_feedback_column(self, cursor):
        """Add feedback column to existing campaigns table if it doesn't exist"""
        try:
            # Check if feedback column exists
            await cursor.execute("PRAGMA table_info(campaigns)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'feedback' not in column_names:
                logger.info("Adding feedback column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN feedback TEXT
                """)
                logger.info("Feedback column added successfully")
        except Exception as e:
            logger.warning(f"Could not add feedback column (may already exist): {e}")
    
    async def migrate_add_scheduling_columns(self, cursor):
        """Add scheduling columns to existing campaigns table if they don't exist"""
        try:
            # Check if scheduling columns exist
            await cursor.execute("PRAGMA table_info(campaigns)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'scheduled_at' not in column_names:
                logger.info("Adding scheduled_at column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN scheduled_at TEXT
                """)
                logger.info("scheduled_at column added successfully")
            
            if 'scheduling_status' not in column_names:
                logger.info("Adding scheduling_status column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN scheduling_status TEXT
                """)
                logger.info("scheduling_status column added successfully")
        except Exception as e:
            logger.warning(f"Could not add scheduling columns (may already exist): {e}")
    
    async def migrate_add_review_columns(self, cursor):
        """Add review columns to existing campaigns table if they don't exist"""
        try:
            # Check if review columns exist
            await cursor.execute("PRAGMA table_info(campaigns)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'review_status' not in column_names:
                logger.info("Adding review_status column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN review_status TEXT
                """)
                logger.info("review_status column added successfully")
            
            if 'reviewer_notes' not in column_names:
                logger.info("Adding reviewer_notes column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN reviewer_notes TEXT
                """)
                logger.info("reviewer_notes column added successfully")
        except Exception as e:
            logger.warning(f"Could not add review columns (may already exist): {e}")
    
    async def migrate_add_performance_columns(self, cursor):
        """Add performance tracking columns to existing campaigns table if they don't exist"""
        try:
            # Check if performance columns exist
            await cursor.execute("PRAGMA table_info(campaigns)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'open_rate' not in column_names:
                logger.info("Adding open_rate column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN open_rate REAL
                """)
                logger.info("open_rate column added successfully")
            
            if 'click_rate' not in column_names:
                logger.info("Adding click_rate column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN click_rate REAL
                """)
                logger.info("click_rate column added successfully")
            
            if 'conversion_rate' not in column_names:
                logger.info("Adding conversion_rate column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN conversion_rate REAL
                """)
                logger.info("conversion_rate column added successfully")
            
            if 'performance_score' not in column_names:
                logger.info("Adding performance_score column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN performance_score REAL
                """)
                logger.info("performance_score column added successfully")
            
            if 'performance_timestamp' not in column_names:
                logger.info("Adding performance_timestamp column to campaigns table")
                await cursor.execute("""
                    ALTER TABLE campaigns ADD COLUMN performance_timestamp TEXT
                """)
                logger.info("performance_timestamp column added successfully")
        except Exception as e:
            logger.warning(f"Could not add performance columns (may already exist): {e}")


# Global database instance
db = Database()


async def get_db():
    """
    Dependency for FastAPI to get database connection.
    Note: For now, we use a single connection. In production, consider connection pooling.
    """
    # Ensure connection exists and is valid
    if not hasattr(db, 'conn') or db.conn is None:
        await db.connect()
    else:
        # Check if connection is still valid by trying to access it
        try:
            # Simple check - if connection is closed, reconnect
            if hasattr(db.conn, '_conn') and db.conn._conn is None:
                await db.connect()
        except (AttributeError, ValueError):
            # Connection is invalid, reconnect
            await db.connect()
    
    # Yield the connection - don't catch exceptions here
    # FastAPI will handle cleanup and exception propagation
    yield db.conn

