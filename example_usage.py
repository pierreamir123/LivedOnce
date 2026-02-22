"""Example usage of the PostgreSQL state management system with LangGraph."""

import asyncio
from typing import Dict, Any, List
from psycopg_pool import AsyncConnectionPool
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from state_manager import PostgreSQLStateManager, LazyLoadedState, LangGraphPostgreSQLSaver
from state_models import MainState


# Example nodes for your LangGraph workflow
async def load_heavy_data_node(state: LazyLoadedState) -> Dict[str, Any]:
    """Node that loads heavy data fields only when needed."""
    # Only load heavy fields if they're not already loaded
    if 'retrieved_docs' not in state.loaded_fields:
        await state.ensure_field_loaded('retrieved_docs')
    
    if 'chat_history' not in state.loaded_fields:
        await state.ensure_field_loaded('chat_history')
    
    # Process the loaded data
    docs_count = len(state.get('retrieved_docs', []))
    history_length = len(state.get('chat_history', []))
    
    print(f"Processing {docs_count} documents with {history_length} chat history entries")
    
    # Return updates to state
    return {
        "processing_metadata": {"docs_processed": docs_count, "history_items": history_length},
        "status": "data_loaded"
    }


async def generate_response_node(state: LazyLoadedState) -> Dict[str, Any]:
    """Node that generates a response based on the state."""
    # Ensure we have the required fields
    required_fields = ['input', 'chat_history', 'retrieved_docs']
    await state.ensure_fields_loaded(required_fields)
    
    # Generate a simple response based on the input
    input_text = state.get('input', '')
    chat_history = state.get('chat_history', [])
    
    response = f"Processed input: '{input_text[:50]}...' with {len(chat_history)} previous messages"
    
    # Update the state
    return {
        "final_response": response,
        "last_answer": response,
        "answer_history": state.get('answer_history', []) + [response],
        "response_generated": True
    }


async def routing_node(state: LazyLoadedState) -> Dict[str, str]:
    """Node that makes routing decisions based on the state."""
    # Load only the fields we need for routing
    await state.ensure_field_loaded('input')
    
    input_text = state.get('input', '').lower()
    
    if any(word in input_text for word in ['query', 'search', 'find']):
        return {"next_node": "search_processing"}
    elif any(word in input_text for word in ['chat', 'talk', 'discuss']):
        return {"next_node": "conversation"}
    else:
        return {"next_node": "default_processing"}


async def search_processing_node(state: LazyLoadedState) -> Dict[str, Any]:
    """Process search-related queries."""
    await state.ensure_fields_loaded(['input', 'user_id'])
    
    # Simulate search processing
    search_results = [{"id": i, "title": f"Result {i}", "score": 0.9-i*0.1} for i in range(5)]
    
    return {
        "generated_query": f"Search query based on: {state.get('input')}",
        "retrieved_docs": search_results,
        "route_decision": "search",
        "execution_path": "search_flow"
    }


async def conversation_node(state: LazyLoadedState) -> Dict[str, Any]:
    """Process conversational inputs."""
    await state.ensure_fields_loaded(['chat_history', 'input'])
    
    # Add the current input to chat history
    new_message = {"role": "user", "content": state.get('input'), "timestamp": "now"}
    updated_history = state.get('chat_history', []) + [new_message]
    
    return {
        "chat_history": updated_history,
        "route_decision": "conversation",
        "execution_path": "conversation_flow"
    }


async def default_processing_node(state: LazyLoadedState) -> Dict[str, Any]:
    """Default processing for unrecognized inputs."""
    await state.ensure_field_loaded('input')
    
    return {
        "final_response": f"I received your input: {state.get('input')[:100]}...",
        "route_decision": "default",
        "execution_path": "default_flow"
    }


def create_graph_with_postgres_state():
    """Create a LangGraph with PostgreSQL-backed state management."""
    
    # Create the graph with our custom state
    graph_builder = StateGraph(MainState)
    
    # Add nodes to the graph
    graph_builder.add_node("routing", routing_node)
    graph_builder.add_node("load_data", load_heavy_data_node)
    graph_builder.add_node("generate_response", generate_response_node)
    graph_builder.add_node("search_processing", search_processing_node)
    graph_builder.add_node("conversation", conversation_node)
    graph_builder.add_node("default_processing", default_processing_node)
    
    # Define conditional edges from routing node
    graph_builder.add_conditional_edges(
        "routing",
        lambda x: x.get("next_node", "default_processing"),
        {
            "search_processing": "search_processing",
            "conversation": "conversation",
            "default_processing": "default_processing"
        }
    )
    
    # Add regular edges
    graph_builder.add_edge("search_processing", "load_data")
    graph_builder.add_edge("conversation", "load_data")
    graph_builder.add_edge("default_processing", "load_data")
    graph_builder.add_edge("load_data", "generate_response")
    
    # Set entry point and finish point
    graph_builder.set_entry_point("routing")
    graph_builder.set_finish_point("generate_response")
    
    return graph_builder.compile()


async def main():
    """Main function demonstrating the PostgreSQL state management."""
    
    # Create connection pool
    pool = AsyncConnectionPool(conninfo="postgresql://username:password@localhost/dbname")
    
    try:
        # Initialize state manager
        state_manager = PostgreSQLStateManager(pool, table_name="graph_state")
        
        # Initialize a lazy-loaded state
        chat_id = "test_chat_123"
        initial_state = {
            "input": "Find information about Python programming",
            "chat_history": [{"role": "user", "content": "Hello", "timestamp": "2023-01-01"}],
            "group_id": 1,
            "user_id": 123,
            "categories": ["programming", "python"],
            "chat_id": chat_id
        }
        
        lazy_state = await state_manager.initialize_state(chat_id, initial_state)
        
        print(f"Initial loaded fields: {lazy_state.loaded_fields}")
        print(f"Initial dirty fields: {lazy_state.dirty_fields}")
        
        # Test field loading
        await lazy_state.ensure_fields_loaded(['input', 'chat_history'])
        print(f"After loading input/chat_history: {lazy_state.loaded_fields}")
        
        # Test individual field access
        await lazy_state.ensure_field_loaded('user_id')
        print(f"User ID: {lazy_state.get('user_id')}")
        
        # Create the graph with PostgreSQL integration
        graph = create_graph_with_postgres_state()
        
        # Create a PostgreSQL saver for checkpoints
        saver = LangGraphPostgreSQLSaver(pool, table_name="graph_checkpoints")
        
        # Configure the run with thread ID
        config = {"configurable": {"thread_id": chat_id}}
        
        # Run the graph
        result = await graph.ainvoke(
            lazy_state._data,  # Pass the underlying data
            config=config
        )
        
        print("Graph execution completed!")
        print(f"Final response: {result.get('final_response', 'No response generated')}")
        
        # Save the updated state back to database
        await lazy_state.update(result)
        await lazy_state.save()
        
        print("State saved to PostgreSQL!")
        
    finally:
        # Clean up resources
        await pool.close()


# Alternative usage with context manager approach
class GraphWithPostgreSQLState:
    """Wrapper class that integrates LangGraph with PostgreSQL state management."""
    
    def __init__(self, pool: AsyncConnectionPool, table_name: str = "graph_state"):
        self.pool = pool
        self.state_manager = PostgreSQLStateManager(pool, table_name)
        self.graph = create_graph_with_postgres_state()
        self.saver = LangGraphPostgreSQLSaver(pool)
    
    async def run_with_state(self, chat_id: str, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run the graph with PostgreSQL-backed state."""
        
        # Initialize state
        lazy_state = await self.state_manager.initialize_state(chat_id, initial_input)
        
        # Prepare configuration
        config = {
            "configurable": {"thread_id": chat_id},
            "checkpoint_saver": self.saver
        }
        
        # Run the graph
        result = await self.graph.ainvoke(lazy_state._data, config=config)
        
        # Update and save state
        lazy_state.update(result)
        await lazy_state.save()
        
        return result
    
    async def stream_with_state(self, chat_id: str, initial_input: Dict[str, Any]):
        """Stream the graph execution with PostgreSQL-backed state."""
        
        # Initialize state
        lazy_state = await self.state_manager.initialize_state(chat_id, initial_input)
        
        # Prepare configuration
        config = {
            "configurable": {"thread_id": chat_id},
            "checkpoint_saver": self.saver
        }
        
        # Stream the graph execution
        async for chunk in self.graph.astream(lazy_state._data, config=config):
            yield chunk


# Example of using the wrapper class
async def example_wrapper_usage():
    """Example of using the GraphWithPostgreSQLState wrapper."""
    
    pool = AsyncConnectionPool(conninfo="postgresql://username:password@localhost/dbname")
    
    try:
        graph_wrapper = GraphWithPostgreSQLState(pool)
        
        initial_input = {
            "input": "What are the best practices for Python development?",
            "chat_history": [],
            "user_id": 456,
            "group_id": 2,
            "chat_id": "wrapper_test_456"
        }
        
        result = await graph_wrapper.run_with_state("wrapper_test_456", initial_input)
        print("Wrapper execution completed!")
        print(f"Result: {result}")
        
        # Example of streaming
        print("\nStreaming example:")
        async for chunk in graph_wrapper.stream_with_state("stream_test_789", initial_input):
            print(f"Chunk: {chunk}")
        
    finally:
        await pool.close()


if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())