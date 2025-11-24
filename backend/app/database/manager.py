"""
Database management utilities and services.
"""

from django.db import connection
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database operations and connections.
    Provides utilities for dynamic queries and data management.
    """
    
    @staticmethod
    def get_database_info() -> Dict[str, Any]:
        """Get information about the current database connection"""
        from django.conf import settings
        db_config = settings.DATABASES['default']
        
        return {
            'engine': db_config['ENGINE'].split('.')[-1],
            'name': db_config['NAME'],
            'host': db_config.get('HOST', 'N/A'),
            'port': db_config.get('PORT', 'N/A'),
        }
    
    @staticmethod
    def execute_raw_query(query: str, params: tuple = None) -> List[Dict]:
        """
        Execute a raw SQL query and return results as list of dicts.
        Use with caution - prefer ORM when possible.
        """
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def get_table_info(table_name: str) -> Dict[str, Any]:
        """Get information about a specific table"""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            cursor.execute(f"PRAGMA table_info({table_name})" 
                         if 'sqlite' in connection.settings_dict['ENGINE'] 
                         else f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            return {
                'table_name': table_name,
                'row_count': row_count,
                'columns': columns
            }
    
    @staticmethod
    def test_connection() -> bool:
        """Test database connection"""
        try:
            connection.ensure_connection()
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
