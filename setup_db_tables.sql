-- SQL script to create required tables for the PostgreSQL state management system

-- Table for storing graph state
CREATE TABLE IF NOT EXISTS graph_state (
    chat_id VARCHAR(255) PRIMARY KEY,
    input TEXT,
    chat_history JSONB DEFAULT '[]',
    group_id INTEGER,
    group_name VARCHAR(255),
    user_id INTEGER,
    categories JSONB DEFAULT '[]',
    route_decision VARCHAR(100),
    final_response TEXT,
    state_metadata JSONB DEFAULT '{}',
    response_metadata JSONB DEFAULT '{}',
    
    -- Document processing fields
    generated_query TEXT,
    original_query TEXT,
    query_type VARCHAR(50),
    execution_path VARCHAR(100),
    optimization_suggestions JSONB DEFAULT '[]',
    retrieved_docs JSONB DEFAULT '[]',
    validated_docs JSONB DEFAULT '[]',
    context TEXT,
    answer TEXT,
    citations JSONB DEFAULT '[]',
    citation_count INTEGER DEFAULT 0,
    
    -- Metadata fields
    retrieval_metadata JSONB DEFAULT '{}',
    validation_metadata JSONB DEFAULT '{}',
    generation_metadata JSONB DEFAULT '{}',
    
    -- Response fields
    listing_response TEXT,
    selection_response TEXT,
    selected_doc JSONB,
    doc_index INTEGER,
    formatted_response TEXT,
    chat_response TEXT,
    
    -- Additional state management fields
    user_email VARCHAR(255),
    client_ids JSONB DEFAULT '[]',
    last_route VARCHAR(100),
    route_history JSONB DEFAULT '[]',
    last_interaction TEXT,
    last_answer TEXT,
    answer_history JSONB DEFAULT '[]',
    additional_context TEXT,
    state_flags JSONB DEFAULT '{}',
    _request_id VARCHAR(255),
    
    -- MCP orchestrator fields
    mcp_initialized BOOLEAN DEFAULT FALSE,
    available_tools JSONB DEFAULT '[]',
    client_status VARCHAR(50),
    agent_status VARCHAR(50),
    selected_tools JSONB DEFAULT '[]',
    tool_reasoning TEXT,
    execution_plan TEXT,
    execution_result TEXT,
    tool_calls JSONB DEFAULT '[]',
    execution_success BOOLEAN DEFAULT FALSE,
    response TEXT,
    mcp_error TEXT,
    tool_selection_error TEXT,
    execution_error TEXT,
    response_formatting_error TEXT,
    tool_responses JSONB DEFAULT '[]',
    agent_result JSONB DEFAULT '{}',
    
    chat_active BOOLEAN DEFAULT TRUE,
    continue_chat BOOLEAN DEFAULT TRUE,
    tool_responses_content TEXT,
    chat_error TEXT,
    
    -- MCP Classification fields
    mcp_classifier JSONB DEFAULT '{}',
    
    -- Candidate management fields
    raw_candidates JSONB DEFAULT '[]',
    candidates_summary TEXT,
    
    -- Pagination fields
    last_search_query TEXT,
    current_page INTEGER DEFAULT 1,
    page_size INTEGER DEFAULT 6,
    has_more_results BOOLEAN DEFAULT FALSE,
    total_results INTEGER DEFAULT 0,
    pagination_requested BOOLEAN DEFAULT FALSE,
    
    -- Context chat fields
    last_chat_response TEXT,
    conversation_type VARCHAR(50),
    
    -- Careers-specific fields
    tool_usage_history JSONB DEFAULT '[]',
    shown_position_ids JSONB DEFAULT '[]',
    chat_metadata JSONB DEFAULT '{}',
    positions JSONB DEFAULT '[]',
    careers_metadata JSONB DEFAULT '{}',
    
    -- CV application fields
    cv_content TEXT,
    cv_filename VARCHAR(255),
    cv_data JSONB DEFAULT '{}',
    cv_analysis_raw JSONB DEFAULT '{}',
    cv_from_s3 BOOLEAN DEFAULT FALSE,
    matched_positions JSONB DEFAULT '[]',
    selected_positions JSONB DEFAULT '[]',
    workflow_type VARCHAR(50),
    provided_email VARCHAR(255),
    status VARCHAR(50),
    next_action VARCHAR(100),
    application_data JSONB DEFAULT '{}',
    application_submitted BOOLEAN DEFAULT FALSE,
    submission_result JSONB DEFAULT '{}',
    submission_results JSONB DEFAULT '[]',
    extracted_position TEXT,
    extracted_email TEXT,
    
    -- Disambiguation fields
    disambiguation_snapshot JSONB,
    awaiting_selection BOOLEAN,
    disambiguated_position JSONB,
    
    -- Insights data
    insights_data JSONB,
    
    -- Authentication error fields
    error JSONB DEFAULT '{}',
    
    -- Data Analysis Agent fields
    input_file_keys JSONB DEFAULT '[]',
    output_file_keys JSONB DEFAULT '[]',
    file_contents JSONB DEFAULT '{}',
    file_schemas JSONB DEFAULT '{}',
    file_modifications JSONB DEFAULT '[]',
    data_analysis_intent VARCHAR(50),
    pandas_operations JSONB DEFAULT '[]',
    message_order INTEGER DEFAULT 0,
    all_available_files JSONB DEFAULT '{}',
    
    -- MCP Data Analysis fields
    mcp_tool VARCHAR(100),
    mcp_context JSONB DEFAULT '{}',
    mcp_result JSONB DEFAULT '{}',
    mcp_output_files JSONB DEFAULT '[]',
    mcp_missing_files_message TEXT,
    
    -- MCP Planning and Streaming fields
    mcp_execution_plan JSONB DEFAULT '[]',
    mcp_current_step INTEGER DEFAULT 0,
    mcp_step_outputs JSONB DEFAULT '{}',
    mcp_plan_communicated BOOLEAN DEFAULT FALSE,
    mcp_success BOOLEAN DEFAULT FALSE,
    
    -- Services-specific fields
    services_intent VARCHAR(50),
    services_user_name VARCHAR(255),
    services_user_email VARCHAR(255),
    services_user_company VARCHAR(255),
    services_data_collection_step VARCHAR(50),
    services_metadata JSONB DEFAULT '{}',
    selector_response TEXT,
    selector_emitted BOOLEAN DEFAULT FALSE,
    selector_event TEXT,
    
    -- Public routing fields
    public_intent_router VARCHAR(50),
    out_of_scope BOOLEAN DEFAULT FALSE,
    
    -- Prompt Editing Graph fields
    supervisor_decision VARCHAR(100),
    selected_client_id INTEGER,
    selected_client_name VARCHAR(255),
    selected_group_id INTEGER,
    selected_group_name VARCHAR(255),
    selected_agent_id INTEGER,
    selected_agent_name VARCHAR(255),
    creation_mode BOOLEAN DEFAULT FALSE,
    parsed_prompt_data JSONB DEFAULT '{}',
    available_clients JSONB DEFAULT '[]',
    available_groups JSONB DEFAULT '[]',
    available_agents JSONB DEFAULT '[]',
    organization_prompt_data JSONB DEFAULT '{}',
    group_prompt_data JSONB DEFAULT '{}',
    prompts_missing BOOLEAN DEFAULT FALSE,
    prompts_loaded BOOLEAN DEFAULT FALSE,
    missing_prompts JSONB DEFAULT '{}',
    save_error TEXT,
    save_results JSONB DEFAULT '{}',
    
    -- DEPRECATED fields (kept for backward compatibility)
    prompt_diffs JSONB,
    merged_final_prompt_preview TEXT,
    confirmation_required BOOLEAN,
    awaiting_save_confirmation BOOLEAN,
    save_confirmed BOOLEAN,
    
    -- Prompt editing ReAct agent fields
    prompt_agent_initialized BOOLEAN DEFAULT FALSE,
    prompt_agent_tool_calls JSONB DEFAULT '[]',
    prompt_agent_tool_responses JSONB DEFAULT '[]',
    prompt_agent_plan TEXT,
    prompt_agent_response TEXT,
    prompt_agent_error TEXT,
    
    -- Memory tool fields
    memory_context JSONB DEFAULT '{}',
    memory_summary TEXT,
    memory_metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_graph_state_user_id ON graph_state(user_id);
CREATE INDEX IF NOT EXISTS idx_graph_state_group_id ON graph_state(group_id);
CREATE INDEX IF NOT EXISTS idx_graph_state_updated_at ON graph_state(updated_at);

-- Trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_graph_state_updated_at 
    BEFORE UPDATE ON graph_state 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Table for storing graph checkpoints
CREATE TABLE IF NOT EXISTS graph_checkpoints (
    thread_id VARCHAR(255) PRIMARY KEY,
    checkpoint JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    versions JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for checkpoints table
CREATE INDEX IF NOT EXISTS idx_graph_checkpoints_updated_at ON graph_checkpoints(updated_at);

-- Insert a sample record to test the table
INSERT INTO graph_state (chat_id, input, user_id, group_id, chat_history, created_at, updated_at)
VALUES (
    'sample_chat_001', 
    'Hello, how can you help me?', 
    123, 
    1, 
    '[{"role": "user", "content": "Hello, how can you help me?", "timestamp": "2023-01-01T10:00:00Z"}]', 
    CURRENT_TIMESTAMP, 
    CURRENT_TIMESTAMP
)
ON CONFLICT (chat_id) DO NOTHING;

-- Show table structure
\d graph_state;