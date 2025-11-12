"""
Scheduler service for processing scheduled campaigns
Runs as a background task to check and update scheduled campaigns
"""
import asyncio
from datetime import datetime
from typing import Optional
import logging

from app.database import db
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled campaigns"""
    
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.check_interval = 60  # Check every 60 seconds
    
    async def start(self):
        """Start the scheduler background task"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info("Scheduler service started")
    
    async def stop(self):
        """Stop the scheduler background task"""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler service stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._check_scheduled_campaigns()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            
            # Wait before next check
            await asyncio.sleep(self.check_interval)
    
    async def _check_scheduled_campaigns(self):
        """Check for campaigns that need to be processed"""
        try:
            # Ensure database connection
            if not hasattr(db, 'conn') or db.conn is None:
                await db.connect()
            
            conn = db.conn
            
            # Get campaigns that are scheduled and past their scheduled time
            past_campaigns = await Campaign.get_past_scheduled_campaigns(conn)
            
            if not past_campaigns:
                return
            
            logger.info(f"Found {len(past_campaigns)} scheduled campaigns to process")
            
            for campaign in past_campaigns:
                try:
                    # Update scheduling status to 'sent'
                    # Note: Actual email sending is out of scope for MVP
                    await campaign.update(
                        conn,
                        scheduling_status='sent'
                    )
                    
                    logger.info(
                        f"Marked campaign {campaign.id} ({campaign.campaign_name}) "
                        f"as sent (scheduled for {campaign.scheduled_at})"
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing scheduled campaign {campaign.id}: {e}",
                        exc_info=True
                    )
        
        except Exception as e:
            logger.error(f"Error checking scheduled campaigns: {e}", exc_info=True)


# Global scheduler instance
scheduler_service = SchedulerService()

