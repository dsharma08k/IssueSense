"""Supabase database client setup"""

from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """Supabase database client wrapper"""
    
    def __init__(self):
        self._client: Client | None = None
    
    @property
    def client(self) -> Client:
        """Get or create Supabase client"""
        if self._client is None:
            try:
                self._client = create_client(
                    settings.supabase_url,
                    settings.supabase_anon_key
                )
                logger.info("✅ Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                raise
        return self._client
    
    def get_user_client(self, access_token: str) -> Client:
        """Create Supabase client with user's JWT token for RLS"""
        try:
            client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            # Set the user's auth token
            client.auth.set_session(access_token, access_token)
            return client
        except Exception as e:
            logger.error(f"❌ Failed to create user client: {e}")
            raise
    
    @property
    def admin_client(self) -> Client:
        """Get Supabase client with service role (admin) privileges"""
        try:
            return create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase admin client: {e}")
            raise


# Global database instance
db = Database()


def get_db() -> Client:
    """Dependency for getting database client"""
    return db.client


def get_admin_db() -> Client:
    """Dependency for getting admin database client"""
    return db.admin_client
