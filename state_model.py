"""State models for the orchestration graphs."""

from typing import Dict, Any, List, TypedDict, NotRequired


class MainState(TypedDict):
    """Enhanced main state for the complete chat system with database-driven prompts."""

    input: str
    chat_history: List
    group_id: int
    group_name: str
    user_id: int
    chat_id: str
    categories: List[str]
    route_decision: str
    final_response: str
    state_metadata: Dict[str, Any]
    response_metadata: Dict[str, Any]

    # Document processing fields
    generated_query: str
    original_query: str
    query_type: str
    execution_path: str
    optimization_suggestions: List[str]
    retrieved_docs: List
    validated_docs: List
    context: str
    answer: str
    citations: List[Dict[str, Any]]  # Citation metadata for retrieved documents
    citation_count: int  # Number of citations available

    # Metadata fields for tracking processing steps
    retrieval_metadata: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    generation_metadata: Dict[str, Any]

    # Response fields for different workflows
    listing_response: str
    selection_response: str
    selected_doc: Any
    doc_index: int
    formatted_response: str
    chat_response: str

    # Additional state management fields
    user_email: str
    client_ids: List[int]  # List of client IDs user has access to
    last_route: str
    route_history: List[str]
    last_interaction: str
    last_answer: str
    answer_history: List[str]
    additional_context: str
    state_flags: Dict[str, Any]
    _request_id: str

    # MCP orchestrator fields
    mcp_initialized: bool
    available_tools: List[Dict[str, Any]]
    client_status: str
    agent_status: str
    selected_tools: List[str]
    tool_reasoning: str
    execution_plan: str  # Execution plan text (not a list)
    execution_result: str
    tool_calls: List[Any]
    execution_success: bool
    response: str
    mcp_error: str
    tool_selection_error: str
    execution_error: str
    response_formatting_error: str
    tool_responses: List[Dict[str, Any]]
    agent_result: Dict[str, Any]

    chat_active: bool
    continue_chat: bool
    tool_responses_content: str
    chat_error: str

    # MCP Classification fields (LLM-based intelligent classification)
    mcp_classifier: Dict[
        str, Any
    ]  # Contains: classification, reasoning, has_context, etc.

    # Candidate management fields
    raw_candidates: List[Dict[str, Any]]  # Raw candidate data from tool responses
    candidates_summary: str  # Formatted markdown summary of candidates for LLM context

    # Pagination fields for candidate search
    last_search_query: str  # Original search query for pagination
    current_page: int  # Current page number (1-indexed)
    page_size: int  # Number of results per page (default: 6)
    has_more_results: bool  # Whether more results are available
    total_results: int  # Total number of results (if available)
    pagination_requested: bool  # Flag indicating user requested more results

    # Context chat fields
    last_chat_response: str  # Last response from context chat agent
    conversation_type: str  # Type of conversation: "context_chat", "new_search", etc.

    # Careers-specific fields for dynamic tool tracking
    tool_usage_history: List[
        Dict[str, Any]
    ]  # Track all tool calls: [{tool: "get_available_positions", params: {...}, timestamp: ...}]
    shown_position_ids: List[str]  # IDs of positions already shown to avoid repetition
    # Note: All other tool parameters are automatically tracked as last_{param_name} dynamically
    chat_metadata: Dict[str, Any]  # Metadata about chat interactions
    positions: List[Dict[str, Any]]
    careers_metadata: Dict[str, Any]

    # CV application fields for careers workflow
    cv_content: (
        str  # Sanitized CV text content (base64 decoded, sanitized to 10K chars max)
    )
    cv_filename: str  # Original filename of the uploaded CV
    cv_data: Dict[str, Any]  # Extracted CV analysis data (from external service)
    cv_analysis_raw: Dict[str, Any]  # Raw response from CV analysis service
    cv_from_s3: bool  # Whether CV was loaded from S3 storage
    matched_positions: List[Dict[str, Any]]  # CV-matched positions with percentages
    selected_positions: List[Dict[str, Any]]  # User-selected positions for application
    workflow_type: str  # Workflow routing: "chat" or "apply_cv"
    provided_email: str  # Email provided by user for CV application
    status: str  # Application status: "awaiting_position", "awaiting_email", "application_submitted"
    next_action: str  # Next action required from user
    application_data: Dict[str, Any]  # CV application data for submission
    application_submitted: bool  # Whether application was successfully submitted
    submission_result: Dict[str, Any]  # Result from single application submission
    submission_results: List[
        Dict[str, Any]
    ]  # Results from multiple application submissions
    extracted_position: str
    extracted_email: str

    # Disambiguation fields for duplicate job title handling (optional)
    disambiguation_snapshot: NotRequired[
        Dict[str, Any]
    ]  # Snapshot of positions with duplicate titles (serialized DisambiguationSnapshot)
    awaiting_selection: NotRequired[
        bool
    ]  # Whether system is awaiting user to select from disambiguation list
    disambiguated_position: NotRequired[
        Dict[str, Any]
    ]  # The position selected by user after disambiguation

    # Insights data for MCP insights processing
    insights_data: Any

    # Authentication error fields
    error: Dict[str, Any]

    # Data Analysis Agent fields
    input_file_keys: List[str]  # S3 keys of files attached to request
    output_file_keys: List[str]  # S3 keys of files generated in response
    file_contents: Dict[str, Any]  # Loaded file data (DataFrames as dict, PDF text)
    file_schemas: Dict[
        str, Any
    ]  # Schema info for each file (columns, types, row count)
    file_modifications: List[Dict[str, Any]]  # Track what was modified
    data_analysis_intent: str  # Detected intent: read, modify, compare, aggregate
    pandas_operations: List[str]  # List of pandas operations to execute
    message_order: (
        int  # Order number of response message in chat (for output file paths)
    )
    all_available_files: Dict[
        str, Any
    ]  # All files available: current, previous_inputs, previous_outputs
    error: Dict[str, Any]

    # MCP Data Analysis fields (for telecom billing MCP tools)
    mcp_tool: str  # MCP tool to use: "auto_classifier", "none", etc.
    mcp_context: Dict[str, Any]  # Context for MCP tool execution
    mcp_result: Dict[str, Any]  # Result from MCP tool execution
    mcp_output_files: List[str]  # S3 keys of files generated by MCP
    mcp_missing_files_message: str  # Message when required files are missing

    # MCP Planning and Streaming fields (for sequential execution with output chaining)
    mcp_execution_plan: List[Dict[str, Any]]  # Ordered list of execution steps
    mcp_current_step: int  # Current step index in execution plan
    mcp_step_outputs: Dict[
        str, Any
    ]  # Outputs from completed steps (keyed by step index)
    mcp_plan_communicated: bool  # Whether plan has been streamed to user
    mcp_success: bool  # Overall MCP execution success

    # Services-specific fields
    services_intent: str  # Intent: show_services, book_meeting, speak_agent, close_chat, general_chat
    services_user_name: str  # Name collected from user
    services_user_email: str  # Email collected from user
    services_user_company: str  # Company name collected from user
    services_data_collection_step: (
        str  # Current data collection step: name, email, company, completed
    )
    services_metadata: Dict[str, Any]  # Additional services metadata
    selector_response: str  # User's response to selector (choice selected)
    selector_emitted: bool  # Flag indicating selector was emitted to user
    selector_event: str  # The selector event string that was emitted

    # Public routing fields
    public_intent_router: (
        str  # Routing intent for public endpoints: "careers" or "services"
    )
    out_of_scope: bool  # Flag indicating user is asking out-of-scope questions
    message_order: (
        int  # Order number of response message in chat (for output file paths)
    )
    all_available_files: Dict[
        str, Any
    ]  # All files available: current, previous_inputs, previous_outputs

    # Prompt Editing Graph fields
    supervisor_decision: str  # Routing decision from supervisor node
    selected_client_id: int  # Selected client ID for prompt editing
    selected_client_name: str  # Selected client name
    selected_group_id: int  # Selected group ID for prompt editing
    selected_group_name: str  # Selected group name
    selected_agent_id: int  # Selected agent ID for prompt editing
    selected_agent_name: str  # Selected agent name
    creation_mode: bool  # Whether in prompt creation mode
    parsed_prompt_data: Dict[str, Any]  # Parsed prompt data from user input
    available_clients: List[Dict[str, Any]]  # Available clients for selection
    available_groups: List[Dict[str, Any]]  # Available groups for selection
    available_agents: List[Dict[str, Any]]  # Available agents for selection
    organization_prompt_data: Dict[str, Any]  # Organization-level prompt data
    group_prompt_data: Dict[str, Any]  # Group-level prompt data
    prompts_missing: bool  # Whether prompts are missing and need creation
    prompts_loaded: bool  # Whether prompts have been loaded
    missing_prompts: Dict[str, bool]  # Which prompts are missing (org/group)
    save_error: str  # Error message from save operation
    save_results: Dict[str, Any]  # Results from save operation

    # DEPRECATED: Legacy confirmation flow fields (unused in agent-first architecture)
    # These fields were part of the old multi-node supervisor-based workflow
    # The agent-first architecture handles prompts directly without confirmation UI
    prompt_diffs: Dict[str, Any]  # DEPRECATED: Diff previews for org/group prompts
    merged_final_prompt_preview: str  # DEPRECATED: Preview of merged final prompt
    confirmation_required: bool  # DEPRECATED: Whether save confirmation is required
    awaiting_save_confirmation: bool  # DEPRECATED: Whether awaiting user confirmation
    save_confirmed: bool  # DEPRECATED: Whether user confirmed save

    # Prompt editing ReAct agent fields (ACTIVE)
    prompt_agent_initialized: bool  # Whether prompt editing agent is initialized
    prompt_agent_tool_calls: List[Dict[str, Any]]  # Tool calls made by prompt agent
    prompt_agent_tool_responses: List[
        Dict[str, Any]
    ]  # Tool responses from prompt agent
    prompt_agent_plan: str  # Agent's execution plan
    prompt_agent_response: str  # Agent's final response
    prompt_agent_error: str  # Error from agent execution

    # Memory tool fields for big data handling from MCP responses
    memory_context: Dict[str, Any]  # Structured storage of MCP responses with extracted data
    memory_summary: str  # LLM-generated summary of stored data for context
    memory_metadata: Dict[str, Any]  # Timestamps, sources, data types, and other metadata