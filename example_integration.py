"""Example integration of PostgreSQL State Manager with LangGraph."""

import asyncio
from typing import Dict, Any, List
from langgraph.graph import StateGraph
from langgraph.constants import SEND
from postgres_state_manager import PostgreSQLStateManager, create_config
from state_model import MainState


def example_node(state: MainState) -> MainState:
    """Example node that modifies the state."""
    print(f"Processing input: {state['input']}")
    
    # Update some state values
    updated_state = {
        "answer": f"Processed: {state['input']}",
        "route_decision": "processed",
        "last_interaction": "example_node"
    }
    
    return updated_state


def document_processing_node(state: MainState) -> MainState:
    """Node that processes documents and updates related fields."""
    print(f"Processing documents for: {state['original_query']}")
    
    # Simulate document processing
    processed_docs = [
        {"id": 1, "content": "Sample document content", "score": 0.9},
        {"id": 2, "content": "Another sample document", "score": 0.8}
    ]
    
    return {
        "retrieved_docs": processed_docs,
        "context": "Context from processed documents",
        "citation_count": len(processed_docs),
        "query_type": "document_search"
    }


def response_generation_node(state: MainState) -> MainState:
    """Node that generates the final response."""
    print(f"Generating response based on context: {state.get('context', 'No context')}")
    
    # Generate response based on available information
    response = f"Final response to: {state['input']}"
    
    return {
        "final_response": response,
        "chat_response": response,
        "formatted_response": f"**{response}**"
    }


async def main():
    """Main function demonstrating the PostgreSQL state manager with LangGraph."""
    # Create the state manager
    connection_string = "postgresql://user:password@localhost/dbname"
    # Note: In a real application, you'd use a valid connection string
    # For this example, we'll demonstrate the concepts without requiring an actual DB
    
    try:
        # Create the graph
        builder = StateGraph(MainState)
        
        # Add nodes
        builder.add_node("example", example_node)
        builder.add_node("document_processing", document_processing_node)
        builder.add_node("response_generation", response_generation_node)
        
        # Set entry point
        builder.set_entry_point("example")
        
        # Define edges
        builder.add_edge("example", "document_processing")
        builder.add_edge("document_processing", "response_generation")
        builder.set_finish_point("response_generation")
        
        # Compile the graph
        graph = builder.compile()
        
        # Create initial state
        initial_state: MainState = {
            "input": "Hello, world!",
            "chat_history": [],
            "group_id": 1,
            "group_name": "Test Group",
            "user_id": 123,
            "chat_id": "test-chat-123",
            "categories": ["general"],
            "route_decision": "initial",
            "final_response": "",
            "state_metadata": {},
            "response_metadata": {},
            "generated_query": "",
            "original_query": "Hello, world!",
            "query_type": "",
            "execution_path": "",
            "optimization_suggestions": [],
            "retrieved_docs": [],
            "validated_docs": [],
            "context": "",
            "answer": "",
            "citations": [],
            "citation_count": 0,
            "retrieval_metadata": {},
            "validation_metadata": {},
            "generation_metadata": {},
            "listing_response": "",
            "selection_response": "",
            "selected_doc": None,
            "doc_index": 0,
            "formatted_response": "",
            "chat_response": "",
            "user_email": "test@example.com",
            "client_ids": [1],
            "last_route": "",
            "route_history": [],
            "last_interaction": "",
            "last_answer": "",
            "answer_history": [],
            "additional_context": "",
            "state_flags": {},
            "_request_id": "req-123",
            "mcp_initialized": False,
            "available_tools": [],
            "client_status": "active",
            "agent_status": "ready",
            "selected_tools": [],
            "tool_reasoning": "",
            "execution_plan": "",
            "execution_result": "",
            "tool_calls": [],
            "execution_success": False,
            "response": "",
            "mcp_error": "",
            "tool_selection_error": "",
            "execution_error": "",
            "response_formatting_error": "",
            "tool_responses": [],
            "agent_result": {},
            "chat_active": True,
            "continue_chat": True,
            "tool_responses_content": "",
            "chat_error": "",
            "mcp_classifier": {},
            "raw_candidates": [],
            "candidates_summary": "",
            "last_search_query": "",
            "current_page": 1,
            "page_size": 6,
            "has_more_results": False,
            "total_results": 0,
            "pagination_requested": False,
            "last_chat_response": "",
            "conversation_type": "new_search",
            "tool_usage_history": [],
            "shown_position_ids": [],
            "chat_metadata": {},
            "positions": [],
            "careers_metadata": {},
            "cv_content": "",
            "cv_filename": "",
            "cv_data": {},
            "cv_analysis_raw": {},
            "cv_from_s3": False,
            "matched_positions": [],
            "selected_positions": [],
            "workflow_type": "chat",
            "provided_email": "",
            "status": "awaiting_position",
            "next_action": "",
            "application_data": {},
            "application_submitted": False,
            "submission_result": {},
            "submission_results": [],
            "extracted_position": "",
            "extracted_email": "",
            "disambiguation_snapshot": {},
            "awaiting_selection": False,
            "disambiguated_position": {},
            "insights_data": None,
            "error": {},
            "input_file_keys": [],
            "output_file_keys": [],
            "file_contents": {},
            "file_schemas": {},
            "file_modifications": [],
            "data_analysis_intent": "",
            "pandas_operations": [],
            "message_order": 1,
            "all_available_files": {},
            "mcp_tool": "none",
            "mcp_context": {},
            "mcp_result": {},
            "mcp_output_files": [],
            "mcp_missing_files_message": "",
            "mcp_execution_plan": [],
            "mcp_current_step": 0,
            "mcp_step_outputs": {},
            "mcp_plan_communicated": False,
            "mcp_success": False,
            "services_intent": "general_chat",
            "services_user_name": "",
            "services_user_email": "",
            "services_user_company": "",
            "services_data_collection_step": "name",
            "services_metadata": {},
            "selector_response": "",
            "selector_emitted": False,
            "selector_event": "",
            "public_intent_router": "careers",
            "out_of_scope": False,
            "supervisor_decision": "",
            "selected_client_id": 0,
            "selected_client_name": "",
            "selected_group_id": 0,
            "selected_group_name": "",
            "selected_agent_id": 0,
            "selected_agent_name": "",
            "creation_mode": False,
            "parsed_prompt_data": {},
            "available_clients": [],
            "available_groups": [],
            "available_agents": [],
            "organization_prompt_data": {},
            "group_prompt_data": {},
            "prompts_missing": False,
            "prompts_loaded": False,
            "missing_prompts": {},
            "save_error": "",
            "save_results": {},
            "prompt_agent_initialized": False,
            "prompt_agent_tool_calls": [],
            "prompt_agent_tool_responses": [],
            "prompt_agent_plan": "",
            "prompt_agent_response": "",
            "prompt_agent_error": "",
            "memory_context": {},
            "memory_summary": "",
            "memory_metadata": {}
        }
        
        # Create configuration for the run
        config = create_config("test-thread-123")
        
        print("Starting LangGraph run with PostgreSQL state management...")
        
        # Run the graph
        final_state = await graph.ainvoke(initial_state, config=config)
        
        print("\nFinal state keys:", list(final_state.keys())[:10], "...")
        print("Answer:", final_state.get("answer"))
        print("Final response:", final_state.get("final_response"))
        
        # Demonstrate state loading with field subset (lazy loading concept)
        print("\nDemonstrating field subset loading (simulated):")
        # In a real implementation, this would load only specified fields from the database
        important_fields = ["answer", "final_response", "route_decision", "chat_response"]
        filtered_state = {k: v for k, v in final_state.items() if k in important_fields}
        print("Filtered state:", filtered_state)
        
    except Exception as e:
        print(f"Error during execution: {e}")
        print("Note: This example shows the structure. To run with a real database,")
        print("provide a valid PostgreSQL connection string.")


if __name__ == "__main__":
    asyncio.run(main())