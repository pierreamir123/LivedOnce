# LangGraph PostgreSQL State Manager

This project implements a PostgreSQL-backed state manager for LangGraph using the built-in checkpoint methods from `langgraph.checkpoint.postgres`. The implementation supports efficient state management with optional field filtering for improved performance.

## Components

### 1. PostgreSQLStateManager (`postgres_state_manager.py`)

The main class extends `langgraph.checkpoint.postgres.PostgresSaver` to provide enhanced functionality:

- **Built-in Checkpoint Support**: Uses prebuilt langgraph methods for checkpointing
- **State Loading with Field Filtering**: Supports loading only specific fields (conceptual lazy loading)
- **State Updates**: Efficiently update specific state fields
- **Serialization**: Handles non-JSON serializable objects

### 2. State Model (`state_model.py`)

Contains the `MainState` TypedDict with all the fields you specified, providing type safety for your state.

### 3. Integration Example (`example_integration.py`)

Demonstrates how to use the state manager with a LangGraph workflow.

## Usage

```python
from postgres_state_manager import PostgreSQLStateManager, create_config
from state_model import MainState

# Create state manager
state_manager = PostgreSQLStateManager("your-postgres-connection-string")

# Create configuration
config = create_config("unique-thread-id")

# Save state
await state_manager.save_state(config, your_state_dict)

# Load full state
full_state = await state_manager.load_state(config)

# Load specific fields (conceptual lazy loading)
important_fields = ["input", "answer", "final_response"]
partial_state = await state_manager.load_state(config, field_subset=important_fields)
```

## Key Features

1. **Uses Prebuilt LangGraph Methods**: Leverages `langgraph.checkpoint.postgres.PostgresSaver` for reliable checkpoint storage
2. **Field Filtering**: Conceptually supports loading only required fields to improve performance
3. **Proper Serialization**: Handles complex objects that aren't JSON serializable
4. **Integration Ready**: Designed to work seamlessly with LangGraph workflows

## Installation

```bash
pip install langgraph psycopg psycopg-pool
```

## Example Integration

The example integration demonstrates:
- Creating a multi-node LangGraph workflow
- Using the PostgreSQL state manager for checkpointing
- Proper state initialization with all required fields
- Field filtering for performance optimization

To run the example:

```bash
python example_integration.py
```

Note: You'll need a valid PostgreSQL connection string to run with an actual database.
