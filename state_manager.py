"""State management for LangGraph with lazy loading from PostgreSQL."""

import asyncio
import json
from typing import Dict, Any, Optional, Union, List, get_origin, get_args
from datetime import datetime
from psycopg_pool import AsyncConnectionPool
from psycopg import sql
from langchain_core.runnables import RunnableConfig
from contextlib import asynccontextmanager

from .state_models import MainState  # Import your state model


class LazyStateLoader:
    """Handles lazy loading of state from PostgreSQL."""
    
    def __init__(self, pool: AsyncConnectionPool, table_name: str = "graph_state"):
        self.pool = pool
        self.table_name = table_name
    
    async def load_partial_state(self, chat_id: str, fields: List[str]) -> Dict[str, Any]:
        """Load only specific fields from the database."""
        async with self.pool.connection() as conn:
            columns = ", ".join([f'"{field}"' for field in fields])
            query = f"""
                SELECT {columns}
                FROM {self.table_name}
                WHERE chat_id = %s
            """
            result = await conn.execute(query, (chat_id,))
            row = await result.fetchone()
            
            if row:
                return {
                    field: self._deserialize_value(row[i]) 
                    for i, field in enumerate(fields) 
                    if row[i] is not None
                }
            return {}
    
    async def load_full_state(self, chat_id: str) -> Dict[str, Any]:
        """Load the complete state from the database."""
        async with self.pool.connection() as conn:
            query = f"""
                SELECT *
                FROM {self.table_name}
                WHERE chat_id = %s
            """
            result = await conn.execute(query, (chat_id,))
            row = await result.fetchone()
            
            if row:
                # Get column names
                columns = [desc.name for desc in result.description]
                state_dict = {}
                
                for i, col in enumerate(columns):
                    if row[i] is not None:
                        state_dict[col] = self._deserialize_value(row[i])
                
                return state_dict
            return {}
    
    def _deserialize_value(self, value: Any) -> Any:
        """Deserialize JSON values from the database."""
        if isinstance(value, str) and value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value


class PostgreSQLStateManager:
    """State manager for LangGraph with lazy loading from PostgreSQL."""
    
    def __init__(self, pool: AsyncConnectionPool, table_name: str = "graph_state"):
        self.pool = pool
        self.table_name = table_name
        self.loader = LazyStateLoader(pool, table_name)
        self._loaded_fields = set()
        self._state_cache = {}
        self._dirty_fields = set()
    
    async def initialize_state(self, chat_id: str, initial_state: Optional[MainState] = None) -> 'LazyLoadedState':
        """Initialize a new state instance with lazy loading capabilities."""
        if initial_state is None:
            initial_state = {}
        
        # Load existing state from DB if it exists
        existing_state = await self.loader.load_full_state(chat_id)
        combined_state = {**existing_state, **initial_state}
        
        return LazyLoadedState(
            manager=self,
            chat_id=chat_id,
            initial_data=combined_state
        )
    
    async def save_state(self, chat_id: str, state: Dict[str, Any], fields: Optional[List[str]] = None):
        """Save state to PostgreSQL."""
        if fields is None:
            fields_to_save = list(state.keys())
        else:
            fields_to_save = fields
        
        # Prepare values and build dynamic query
        values = []
        update_parts = []
        
        for field in fields_to_save:
            if field in state:
                value = state[field]
                serialized_value = self._serialize_value(value)
                values.extend([serialized_value, chat_id])
                update_parts.append(f'"{field}" = %s')
        
        if not update_parts:
            return  # Nothing to save
        
        # Build upsert query
        set_clause = ", ".join(update_parts)
        placeholders = ", ".join(["%s"] * len(fields_to_save))
        
        query = f"""
            INSERT INTO {self.table_name} (chat_id, {', '.join([f'"{f}"' for f in fields_to_save])})
            VALUES (%s, {placeholders})
            ON CONFLICT (chat_id)
            DO UPDATE SET {set_clause}
        """
        
        async with self.pool.connection() as conn:
            await conn.execute(query, values)
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize values for database storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)


class LazyLoadedState:
    """A state wrapper that provides lazy loading of fields from PostgreSQL."""
    
    def __init__(self, manager: PostgreSQLStateManager, chat_id: str, initial_data: Dict[str, Any]):
        self._manager = manager
        self.chat_id = chat_id
        self._data = initial_data.copy()
        self._loaded_fields = set(initial_data.keys())
        self._dirty_fields = set()
        self._state_type = MainState  # Reference to your state type
    
    async def ensure_field_loaded(self, field_name: str):
        """Ensure a specific field is loaded into memory."""
        if field_name not in self._loaded_fields:
            partial_state = await self._manager.loader.load_partial_state(
                self.chat_id, [field_name]
            )
            self._data.update(partial_state)
            self._loaded_fields.update(partial_state.keys())
    
    async def ensure_fields_loaded(self, field_names: List[str]):
        """Ensure multiple fields are loaded into memory."""
        unloaded_fields = [f for f in field_names if f not in self._loaded_fields]
        if unloaded_fields:
            partial_state = await self._manager.loader.load_partial_state(
                self.chat_id, unloaded_fields
            )
            self._data.update(partial_state)
            self._loaded_fields.update(partial_state.keys())
    
    async def load_all_fields(self):
        """Load all fields from the database."""
        full_state = await self._manager.loader.load_full_state(self.chat_id)
        self._data.update(full_state)
        self._loaded_fields = set(full_state.keys())
    
    def get(self, key: str, default=None):
        """Get a value from state with lazy loading."""
        if key not in self._loaded_fields:
            # For async method, we'd need to handle this differently in practice
            # This is a sync interface, so caller needs to use ensure_field_loaded first
            return default
        return self._data.get(key, default)
    
    def __getitem__(self, key: str):
        """Allow dictionary-style access to state."""
        if key not in self._loaded_fields:
            raise KeyError(f"Field '{key}' not loaded. Use ensure_field_loaded() first.")
        return self._data[key]
    
    def __setitem__(self, key: str, value):
        """Allow dictionary-style assignment to state."""
        self._data[key] = value
        self._dirty_fields.add(key)
        self._loaded_fields.add(key)
    
    def __contains__(self, key: str):
        """Check if key exists in loaded data."""
        return key in self._data
    
    def keys(self):
        """Return keys of loaded data."""
        return self._data.keys()
    
    def values(self):
        """Return values of loaded data."""
        return self._data.values()
    
    def items(self):
        """Return items of loaded data."""
        return self._data.items()
    
    def update(self, other: Dict[str, Any]):
        """Update state with new values."""
        self._data.update(other)
        self._dirty_fields.update(other.keys())
        self._loaded_fields.update(other.keys())
    
    async def save(self, fields: Optional[List[str]] = None):
        """Save dirty fields or specified fields to database."""
        if fields is None:
            fields_to_save = list(self._dirty_fields)
        else:
            fields_to_save = fields
            
        if fields_to_save:
            await self._manager.save_state(self.chat_id, self._data, fields_to_save)
            self._dirty_fields.difference_update(fields_to_save)
    
    def mark_dirty(self, field: str):
        """Mark a field as needing to be saved."""
        self._dirty_fields.add(field)
    
    def is_dirty(self) -> bool:
        """Check if there are unsaved changes."""
        return len(self._dirty_fields) > 0
    
    @property
    def loaded_fields(self) -> set:
        """Return the set of currently loaded fields."""
        return self._loaded_fields.copy()
    
    @property
    def dirty_fields(self) -> set:
        """Return the set of dirty fields."""
        return self._dirty_fields.copy()


# Integration with LangGraph
class LangGraphPostgreSQLSaver:
    """LangGraph checkpoint saver that uses PostgreSQL for persistence."""
    
    def __init__(self, pool: AsyncConnectionPool, table_name: str = "graph_checkpoints"):
        self.pool = pool
        self.checkpoint_table = table_name
        self.state_manager = PostgreSQLStateManager(pool)
    
    async def put(self, config: RunnableConfig, checkpoint, metadata, new_versions):
        """Save checkpoint to database."""
        chat_id = config.get("configurable", {}).get("thread_id", "default")
        
        # Serialize checkpoint data
        checkpoint_data = {
            "checkpoint": self._serialize(checkpoint),
            "metadata": self._serialize(metadata),
            "versions": self._serialize(new_versions),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Save to checkpoints table
        async with self.pool.connection() as conn:
            query = f"""
                INSERT INTO {self.checkpoint_table} (thread_id, checkpoint, metadata, versions, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (thread_id)
                DO UPDATE SET 
                    checkpoint = EXCLUDED.checkpoint,
                    metadata = EXCLUDED.metadata,
                    versions = EXCLUDED.versions,
                    updated_at = EXCLUDED.updated_at
            """
            await conn.execute(
                query,
                (chat_id, checkpoint_data["checkpoint"], checkpoint_data["metadata"], 
                 checkpoint_data["versions"], checkpoint_data["updated_at"])
            )
    
    async def get_tuple(self, config: RunnableConfig):
        """Load checkpoint from database."""
        chat_id = config.get("configurable", {}).get("thread_id", "default")
        
        async with self.pool.connection() as conn:
            query = f"""
                SELECT checkpoint, metadata, versions, updated_at
                FROM {self.checkpoint_table}
                WHERE thread_id = %s
                ORDER BY updated_at DESC
                LIMIT 1
            """
            result = await conn.execute(query, (chat_id,))
            row = await result.fetchone()
            
            if row:
                checkpoint = self._deserialize(row[0])
                metadata = self._deserialize(row[1])
                versions = self._deserialize(row[2])
                updated_at = row[3]
                
                return {
                    "config": config,
                    "checkpoint": checkpoint,
                    "metadata": metadata,
                    "versions": versions,
                    "updated_at": updated_at
                }
        return None
    
    def _serialize(self, obj: Any) -> str:
        """Serialize object to JSON string."""
        return json.dumps(obj, default=str)
    
    def _deserialize(self, data: str) -> Any:
        """Deserialize JSON string to object."""
        if data:
            return json.loads(data)
        return None


# Usage example
async def example_usage():
    """Example of how to use the lazy loading state manager."""
    
    # Create connection pool
    from psycopg_pool import AsyncConnectionPool
    pool = AsyncConnectionPool(conninfo="postgresql://user:password@localhost/dbname")
    
    # Initialize state manager
    state_manager = PostgreSQLStateManager(pool)
    
    # Initialize state for a specific chat
    chat_id = "chat_123"
    initial_state = {"input": "Hello", "group_id": 1, "user_id": 123}
    lazy_state = await state_manager.initialize_state(chat_id, initial_state)
    
    # Ensure specific fields are loaded before accessing them
    await lazy_state.ensure_fields_loaded(["chat_history", "final_response"])
    
    # Now safely access the loaded fields
    chat_history = lazy_state.get("chat_history", [])
    final_response = lazy_state.get("final_response", "")
    
    # Update some fields
    lazy_state["final_response"] = "Updated response"
    lazy_state["answer"] = "New answer"
    
    # Save changes back to database
    await lazy_state.save()
    
    # Close pool when done
    await pool.close()


__all__ = [
    'PostgreSQLStateManager',
    'LazyLoadedState', 
    'LazyStateLoader',
    'LangGraphPostgreSQLSaver'
]