"""
Campaign database model and operations
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json
import uuid
from app.database import db


class Campaign:
    """Campaign model for database operations"""
    
    def __init__(
        self,
        id: str = None,
        campaign_name: str = None,
        advertiser_name: str = None,
        status: str = "draft",
        created_at: str = None,
        approved_at: Optional[str] = None,
        assets_s3_path: Optional[str] = None,
        html_s3_path: Optional[str] = None,
        proof_s3_path: Optional[str] = None,
        ai_processing_data: Optional[Dict[str, Any]] = None,
        updated_at: Optional[str] = None,
        feedback: Optional[str] = None,
        scheduled_at: Optional[str] = None,
        scheduling_status: Optional[str] = None,
        review_status: Optional[str] = None,
        reviewer_notes: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.campaign_name = campaign_name
        self.advertiser_name = advertiser_name
        self.status = status
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.approved_at = approved_at
        self.assets_s3_path = assets_s3_path
        self.html_s3_path = html_s3_path
        self.proof_s3_path = proof_s3_path
        self.ai_processing_data = ai_processing_data or {}
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.feedback = feedback
        self.scheduled_at = scheduled_at
        self.scheduling_status = scheduling_status
        self.review_status = review_status
        self.reviewer_notes = reviewer_notes
    
    @classmethod
    def from_row(cls, row):
        """Create Campaign instance from database row"""
        ai_data = {}
        if row.get('ai_processing_data'):
            try:
                ai_data = json.loads(row['ai_processing_data'])
            except (json.JSONDecodeError, TypeError):
                ai_data = {}
        
        return cls(
            id=row['id'],
            campaign_name=row['campaign_name'],
            advertiser_name=row['advertiser_name'],
            status=row['status'],
            created_at=row['created_at'],
            approved_at=row.get('approved_at'),
            assets_s3_path=row.get('assets_s3_path'),
            html_s3_path=row.get('html_s3_path'),
            proof_s3_path=row.get('proof_s3_path'),
            ai_processing_data=ai_data,
            updated_at=row.get('updated_at'),
            feedback=row.get('feedback'),
            scheduled_at=row.get('scheduled_at'),
            scheduling_status=row.get('scheduling_status'),
            review_status=row.get('review_status'),
            reviewer_notes=row.get('reviewer_notes')
        )
    
    def to_dict(self):
        """Convert campaign to dictionary"""
        return {
            'id': self.id,
            'campaign_name': self.campaign_name,
            'advertiser_name': self.advertiser_name,
            'status': self.status,
            'created_at': self.created_at,
            'approved_at': self.approved_at,
            'assets_s3_path': self.assets_s3_path,
            'html_s3_path': self.html_s3_path,
            'proof_s3_path': self.proof_s3_path,
            'ai_processing_data': self.ai_processing_data,
            'updated_at': self.updated_at,
            'feedback': self.feedback,
            'scheduled_at': self.scheduled_at,
            'scheduling_status': self.scheduling_status,
            'review_status': self.review_status,
            'reviewer_notes': self.reviewer_notes
        }
    
    async def save(self, conn):
        """Save campaign to database"""
        # Ensure connection is valid
        if conn is None:
            raise ValueError("Database connection is None")
        
        async with conn.cursor() as cursor:
            await cursor.execute("""
                INSERT OR REPLACE INTO campaigns 
                (id, campaign_name, advertiser_name, status, created_at, 
                 approved_at, assets_s3_path, html_s3_path, proof_s3_path, 
                 ai_processing_data, updated_at, feedback, scheduled_at, scheduling_status, 
                 review_status, reviewer_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.id,
                self.campaign_name,
                self.advertiser_name,
                self.status,
                self.created_at,
                self.approved_at,
                self.assets_s3_path,
                self.html_s3_path,
                self.proof_s3_path,
                json.dumps(self.ai_processing_data) if self.ai_processing_data else None,
                self.updated_at,
                self.feedback,
                self.scheduled_at,
                self.scheduling_status,
                self.review_status,
                self.reviewer_notes
            ))
            await conn.commit()
    
    async def update(self, conn, **kwargs):
        """Update campaign fields"""
        self.updated_at = datetime.utcnow().isoformat()
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Save to database
        await self.save(conn)
    
    @staticmethod
    async def get_by_id(conn, campaign_id: str):
        """Get campaign by ID"""
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns WHERE id = ?
            """, (campaign_id,))
            row = await cursor.fetchone()
            
            if row:
                return Campaign.from_row(dict(row))
            return None
    
    @staticmethod
    async def get_all(conn, limit: int = 100, offset: int = 0):
        """Get all campaigns with pagination"""
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = await cursor.fetchall()
            
            return [Campaign.from_row(dict(row)) for row in rows]
    
    @staticmethod
    async def get_by_status(conn, status: str, limit: int = 100, offset: int = 0):
        """Get campaigns by status with pagination"""
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns 
                WHERE status = ?
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (status, limit, offset))
            rows = await cursor.fetchall()
            
            return [Campaign.from_row(dict(row)) for row in rows]
    
    @staticmethod
    async def get_by_review_status(conn, review_status: str, limit: int = 100, offset: int = 0):
        """Get campaigns by review status with pagination"""
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns 
                WHERE review_status = ?
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (review_status, limit, offset))
            rows = await cursor.fetchall()
            
            return [Campaign.from_row(dict(row)) for row in rows]
    
    @staticmethod
    async def get_scheduled_campaigns(conn):
        """Get all campaigns with scheduling_status = 'scheduled' and scheduled_at in the future"""
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns 
                WHERE scheduling_status = 'scheduled' 
                AND scheduled_at IS NOT NULL
                AND scheduled_at > datetime('now')
                ORDER BY scheduled_at ASC
            """)
            rows = await cursor.fetchall()
            
            return [Campaign.from_row(dict(row)) for row in rows]
    
    @staticmethod
    async def get_past_scheduled_campaigns(conn):
        """Get campaigns that were scheduled but the scheduled time has passed"""
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns 
                WHERE scheduling_status = 'scheduled' 
                AND scheduled_at IS NOT NULL
                AND scheduled_at <= datetime('now')
                ORDER BY scheduled_at ASC
            """)
            rows = await cursor.fetchall()
            
            return [Campaign.from_row(dict(row)) for row in rows]

