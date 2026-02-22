# PostgreSQL State Manager for LangGraph

This project implements a sophisticated state management system for LangGraph with lazy loading capabilities from PostgreSQL. It's designed to efficiently handle large state objects by loading only the required fields when needed.

## Features

- **Lazy Loading**: Load only specific fields from the database when needed
- **Efficient Storage**: Store complex state objects in PostgreSQL using JSONB fields
- **Dirty Tracking**: Automatically track which fields have been modified
- **LangGraph Integration**: Seamless integration with LangGraph checkpoint system
- **Type Safety**: Full type hints support with TypedDict definitions

## Components

### 1. LazyStateLoader
Handles the actual loading of state data from PostgreSQL:

```python
loader = LazyStateLoader(pool, table_name="graph_state")

# Load only specific fields
partial_state = await loader.load_partial_state(chat_id, ["chat_history", "final_response"])

# Load complete state
full_state = await loader.load_full_state(chat_id)
```

### 2. PostgreSQLStateManager
Manages the overall state lifecycle and coordinates with the loader:

```python
state_manager = PostgreSQLStateManager(pool)

# Initialize state for a specific chat
lazy_state = await state_manager.initialize_state(chat_id, initial_state)
```

### 3. LazyLoadedState
The main state wrapper that provides the lazy loading functionality:

```python
# Ensure specific fields are loaded
await lazy_state.ensure_fields_loaded(["chat_history", "retrieved_docs"])

# Access loaded fields
chat_history = lazy_state.get("chat_history", [])

# Update fields (automatically marked as dirty)
lazy_state["final_response"] = "New response"

# Save changes back to database
await lazy_state.save()
```

### 4. LangGraphPostgreSQLSaver
Integration with LangGraph's checkpoint system:

```python
saver = LangGraphPostgreSQLSaver(pool)
config = {"configurable": {"thread_id": chat_id}, "checkpoint_saver": saver}
```

## Database Schema

The system uses two main tables:

1. `graph_state` - Stores the actual state data
2. `graph_checkpoints` - Stores LangGraph checkpoints

See `setup_db_tables.sql` for the complete schema definition.

## Usage Examples

### Basic Usage

```python
import asyncio
from psycopg_pool import AsyncConnectionPool
from state_manager import PostgreSQLStateManager

async def main():
    # Create connection pool
    pool = AsyncConnectionPool(conninfo="postgresql://user:pass@localhost/db")
    
    try:
        # Initialize state manager
        state_manager = PostgreSQLStateManager(pool)
        
        # Initialize state for a specific chat
        chat_id = "chat_123"
        initial_state = {
            "input": "Hello",
            "chat_history": [],
            "user_id": 123
        }
        
        lazy_state = await state_manager.initialize_state(chat_id, initial_state)
        
        # Load specific fields when needed
        await lazy_state.ensure_fields_loaded(["retrieved_docs", "context"])
        
        # Work with the state
        retrieved_docs = lazy_state.get("retrieved_docs", [])
        
        # Update state
        lazy_state["final_response"] = "Response here"
        
        # Save changes
        await lazy_state.save()
        
    finally:
        await pool.close()

asyncio.run(main())
```

### With LangGraph

```python
from langgraph.graph import StateGraph
from state_manager import LangGraphPostgreSQLSaver
from state_models import MainState

# Create your nodes
async def my_node(state):
    # Ensure needed fields are loaded
    await state.ensure_field_loaded('input')
    
    # Process and return updates
    return {"processed_input": f"Processed: {state.get('input')}"} 

# Build graph
graph_builder = StateGraph(MainState)
graph_builder.add_node("my_node", my_node)
graph_builder.add_edge("__start__", "my_node")
graph_builder.add_edge("my_node", "__end__")

graph = graph_builder.compile()

# Run with checkpoint saving
saver = LangGraphPostgreSQLSaver(pool)
config = {"configurable": {"thread_id": "chat_123"}, "checkpoint_saver": saver}

result = await graph.ainvoke({"input": "test"}, config=config)
```

## Benefits

1. **Performance**: Only loads the data you actually need
2. **Scalability**: Efficiently handles large state objects
3. **Memory Management**: Reduces memory footprint by loading on demand
4. **Persistence**: Automatic saving of state changes to PostgreSQL
5. **Compatibility**: Works seamlessly with existing LangGraph applications

## Setup

1. Install dependencies:
   ```bash
   pip install psycopg psycopg-pool langgraph langchain-core
   ```

2. Set up database tables:
   ```sql
   psql -h localhost -U username -d database -f setup_db_tables.sql
   ```

3. Use the state manager in your application as shown in the examples above.

This implementation provides a robust foundation for managing complex state in LangGraph applications while maintaining efficiency through lazy loading from PostgreSQL.