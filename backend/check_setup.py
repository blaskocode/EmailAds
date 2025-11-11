#!/usr/bin/env python3
"""
Quick setup checker for EmailAds backend
Run this to verify your environment is configured correctly
"""
import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("❌ .env file not found!")
        print(f"   Expected at: {env_path}")
        print("   Create it from .env.example")
        return False
    print("✅ .env file exists")
    return True

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET_NAME",
        "AWS_REGION"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"❌ {var} is not set")
        else:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var:
                masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                print(f"✅ {var} is set ({masked})")
            else:
                print(f"✅ {var} is set ({value})")
    
    if missing:
        print(f"\n❌ Missing {len(missing)} required environment variables")
        return False
    return True

def check_database():
    """Check if database directory exists and is writable"""
    db_path = Path(__file__).parent.parent / "data"
    try:
        db_path.mkdir(parents=True, exist_ok=True)
        test_file = db_path / ".test_write"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Database directory is writable")
        return True
    except Exception as e:
        print(f"❌ Database directory error: {e}")
        return False

def check_s3_connection():
    """Check S3 connection"""
    try:
        import boto3
    except ImportError:
        print("❌ boto3 not installed. Install with: pip install boto3")
        return False
    
    try:
        from app.config import settings
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Try to head the bucket
        s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        print(f"✅ S3 bucket '{settings.S3_BUCKET_NAME}' is accessible")
        return True
    except Exception as e:
        print(f"❌ S3 connection error: {e}")
        print("   Check your AWS credentials and bucket name")
        return False

def check_openai_key():
    """Check OpenAI API key format"""
    try:
        from app.config import settings
        key = settings.OPENAI_API_KEY
        if key.startswith("sk-") and len(key) > 20:
            print("✅ OpenAI API key format looks valid")
            return True
        else:
            print("⚠️  OpenAI API key format may be invalid (should start with 'sk-')")
            return False
    except Exception as e:
        print(f"❌ Error checking OpenAI key: {e}")
        print("   Make sure all required environment variables are set")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("EmailAds Backend Setup Checker")
    print("=" * 60)
    print()
    
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            # Fallback: manually parse .env file
            print("⚠️  python-dotenv not installed, manually parsing .env file...")
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value:
                                os.environ[key] = value
            except Exception as e:
                print(f"⚠️  Could not parse .env file: {e}")
                print("   Install python-dotenv: pip install python-dotenv")
            print()
    
    results = []
    
    print("1. Checking .env file...")
    results.append(check_env_file())
    print()
    
    print("2. Checking environment variables...")
    results.append(check_env_vars())
    print()
    
    print("3. Checking database directory...")
    results.append(check_database())
    print()
    
    if all(results[:3]):  # Only check S3 and OpenAI if basic setup is OK
        print("4. Checking S3 connection...")
        results.append(check_s3_connection())
        print()
        
        print("5. Checking OpenAI API key...")
        results.append(check_openai_key())
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ All checks passed! Your setup looks good.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

