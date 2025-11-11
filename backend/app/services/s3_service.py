"""
AWS S3 service for file storage
"""
import boto3
import asyncio
from botocore.exceptions import ClientError, BotoCoreError
from typing import Optional, BinaryIO
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """Service for interacting with AWS S3"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def upload_file(
        self,
        file_obj: BinaryIO,
        s3_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to S3 (runs in thread pool to avoid blocking)
        
        Args:
            file_obj: File-like object to upload
            s3_key: S3 object key (path)
            content_type: MIME type of the file
            
        Returns:
            S3 URL of uploaded file
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Reset file pointer to beginning
            file_obj.seek(0)
            
            # Run blocking boto3 operation in thread pool
            await asyncio.to_thread(
                self.s3_client.upload_fileobj,
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            url = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"File uploaded to S3: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise Exception(f"Failed to upload file to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            raise
    
    async def get_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate presigned URL for S3 object (runs in thread pool)
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3 (runs in thread pool)
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"File deleted from S3: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
    
    async def file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3 (runs in thread pool)
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            await asyncio.to_thread(
                self.s3_client.head_object,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    async def test_connection(self) -> bool:
        """
        Test S3 connection and bucket access (runs in thread pool)
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to head bucket (requires ListBucket permission)
            await asyncio.to_thread(
                self.s3_client.head_bucket,
                Bucket=self.bucket_name
            )
            logger.info(f"S3 connection test successful for bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == '404':
                logger.error(f"S3 bucket not found: {self.bucket_name}")
            else:
                logger.error(f"S3 connection test failed: {e}")
            return False
        except BotoCoreError as e:
            logger.error(f"S3 connection error: {e}")
            return False


# Global S3 service instance
s3_service = S3Service()

