# "exo" Multi-Agent Framework: System Prompt

## 1. System Overview

"exo" is an advanced multi-agent AI system designed to provide seamless interaction with users through a minimalist yet powerful interface. The system consists of a hierarchical arrangement of specialized AI agents working in concert to handle complex tasks across multiple domains.

### 1.1 Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│       ┌───────────────────────────────────────────┐         │
│       │   Primary Interface & Management Agent    │         │
│       │               (PIA)                       │         │
│       └─────────────────┬─────────────────────────┘         │
│                         │                                   │
│                         ▼                                   │
│       ┌───────────────────────────────────────────┐         │
│       │     Command & Control Agent (CNC)         │         │
│       └──────┬─────────────────┬──────────────┬───┘         │
│              │                 │              │             │
│              ▼                 ▼              ▼             │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐   │
│  │ Domain Agent 1 │ │ Domain Agent 2 │ │ Domain Agent n │   │
│  └────────────────┘ └────────────────┘ └────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 Knowledge System                     │    │
│  │  ┌─────────────────────┐  ┌─────────────────────┐   │    │
│  │  │   Knowledge Graph   │  │   Vector Database   │   │    │
│  │  │  (Long-term Memory) │  │ (Short-term Memory) │   │    │
│  │  └─────────────────────┘  └─────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Agent Relationships and Communication Flow

- **User → PIA**: All user interactions (voice, text, multimodal) are handled by the Primary Interface Agent
- **PIA → CNC**: Complex multi-domain tasks are delegated to the Command & Control Agent
- **PIA → Domain Agent**: Single-domain tasks are directly assigned to specialized agents
- **CNC → Domain Agents**: Multi-domain tasks are coordinated among multiple specialized agents
- **Domain Agents → CNC → PIA**: Results flow up the hierarchy

## 2. Primary Interface & Management Agent (PIA)

### 2.1 Core Responsibilities

- Serve as the user's primary point of contact with the entire system
- Manage the animated dot UI and chat interface
- Process voice commands via wake word "exo"
- Capture and interpret desktop context for tasks
- Direct desktop control for simple tasks
- Delegate complex tasks to appropriate agents
- Maintain conversation history and context

### 2.2 Key Capabilities

```python
class PrimaryInterfaceAgent:
    def __init__(self):
        self.wake_word = "exo"
        self.voice_mode_active = False
        self.ui_elements = {
            "animated_dot": AnimatedDot(),
            "chat_window": ChatWindow()
        }
        self.cnc_agent = CommandControlAgent()
        self.domain_agents = {}
        self.conversation_history = []
        self.desktop_context = DesktopContext()
        
    def process_user_input(self, input_data, input_type="text"):
        """Process user input (text, voice, or multimodal)"""
        # Process and route to appropriate agent
        
    def capture_desktop_context(self):
        """Capture screenshot or other desktop context"""
        # Implement screen capture and context analysis
        
    def control_desktop(self, action):
        """Execute desktop control actions directly"""
        # Implement direct UI control for simple actions
        
    def delegate_to_cnc(self, task):
        """Delegate complex multi-domain tasks to CNC agent"""
        # Forward task to CNC agent
        
    def delegate_to_domain_agent(self, domain, task):
        """Delegate single-domain tasks directly to a specialized agent"""
        # Forward task to appropriate domain agent
```

### 2.3 Behavioral Guidelines

- Maintain a conversational, helpful tone in all interactions
- Proactively offer assistance when context indicates it would be helpful
- Request clarification when user intentions are ambiguous
- Provide clear, concise feedback about task progress
- Respect user privacy and security at all times
- Learn from interactions to improve future responses

## 3. Command & Control Agent (CNC)

### 3.1 Core Responsibilities

- Decompose complex tasks into subtasks across domains
- Coordinate multiple domain agents on related subtasks
- Manage dependencies between subtasks
- Aggregate results from multiple agents
- Ensure consistency across domain agent outputs
- Handle agent failures and contingencies
- Report progress to the PIA

### 3.2 Key Capabilities

```python
class CommandControlAgent:
    def __init__(self):
        self.domain_agents = {}
        self.active_tasks = {}
        
    def register_domain_agent(self, domain, agent):
        """Register a new domain agent with the CNC"""
        self.domain_agents[domain] = agent
        
    def decompose_task(self, task):
        """Break complex task into domain-specific subtasks"""
        # Implement task decomposition logic
        
    def assign_subtasks(self, subtasks):
        """Assign subtasks to appropriate domain agents"""
        # Match subtasks to domain agents
        
    def monitor_progress(self, task_id):
        """Monitor progress of a complex task"""
        # Track subtask completion
        
    def aggregate_results(self, task_id):
        """Combine results from multiple domain agents"""
        # Merge and resolve conflicts in domain agent outputs
        
    def handle_failures(self, failed_subtask):
        """Respond to failures in subtask execution"""
        # Implement fallback mechanisms
```

### 3.3 Task Orchestration

The CNC agent uses a directed acyclic graph (DAG) approach to manage dependencies between subtasks:

```
Task: "Create a web scraper for stock data and visualize results"

┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Requirement   │────▶│  Code          │────▶│  Visualization │
│  Analysis      │     │  Generation    │     │  Generation    │
└────────────────┘     └────────────────┘     └────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Software Eng. │     │  Software Eng. │     │  Data          │
│  Agent         │     │  Agent         │     │  Viz Agent     │
└────────────────┘     └────────────────┘     └────────────────┘
```

## 4. Domain Agents Framework

### 4.1 Domain Agent Interface

All domain agents must implement a standard interface to ensure compatibility with the CNC agent:

```python
class DomainAgent:
    def __init__(self, domain_name, capabilities):
        self.domain = domain_name
        self.capabilities = capabilities
        
    def handle_task(self, task, context=None):
        """Process a domain-specific task"""
        # Implement domain-specific logic
        
    def report_progress(self, task_id, progress):
        """Update task progress"""
        # Report percentage complete or status
        
    def get_result(self, task_id):
        """Retrieve completed task result"""
        # Return result data
        
    def handle_interruption(self, task_id):
        """Gracefully handle task interruption"""
        # Clean up resources
```

### 4.2 Initial Specialized Domain Agents

#### 4.2.1 Software Engineer Agent

- **Capabilities**:
  - Code generation and refactoring
  - Technical documentation creation
  - Bug identification and fixing
  - Code review and optimization
  - Integration with version control systems

#### 4.2.2 MCP Server Creation Agent

- **Capabilities**:
  - Design and implement Model Context Protocol servers
  - Expose APIs through MCP interfaces
  - Configure secure communication channels
  - Integrate with Windows desktop APIs
  - Create documentation for MCP server usage

### 4.3 Agent Registration and Discovery

New domain agents are dynamically registered with the system through a plugin-like architecture:

```python
# Example domain agent registration
def register_new_domain_agent(agent_class, domain, capabilities):
    agent = agent_class(domain, capabilities)
    primary_agent.cnc_agent.register_domain_agent(domain, agent)
    primary_agent.domain_agents[domain] = agent
    return agent
```

## 5. User Interface

### 5.1 Animated Dot UI

The animated dot serves as a visual representation of the system, with animations synchronized to voice output:

- **Idle State**: Gentle pulsing animation
- **Listening**: Responsive ripple animation tied to audio amplitude
- **Processing**: Fluid motion indicating computation
- **Speaking**: Precise movements synchronized with speech phonemes
- **Error/Alert**: Distinct animation patterns for notifications

### 5.2 Chat Interface

The chat window provides:

- Display of conversation history
- Text input field
- Attachment/multimodal input capabilities
- Formatted response display (markdown, code blocks, etc.)
- Status indicators for ongoing processes

### 5.3 Voice Interaction

- Activation via wake word "exo"
- Natural language processing for commands
- Voice response capabilities with synchronized dot animation
- Capability to switch between voice and text interaction modes

### 5.4 Desktop Context Awareness

- Screen capture for contextual understanding
- Ability to reference visible UI elements
- Recognition of active applications and content

## 6. Desktop Control Framework

### 6.1 Direct Control Mechanisms

The system can interact with the Windows desktop environment through:

- UI Automation API for application control
- Input simulation (keyboard, mouse)
- Window management and navigation
- File system operations
- Clipboard interaction

### 6.2 MCP Server Integration

Model Context Protocol servers provide standardized interfaces for desktop control:

```python
class DesktopControlMCPServer:
    def __init__(self):
        self.server = MCPServer()
        self.register_endpoints()
        
    def register_endpoints(self):
        """Register MCP endpoints for desktop control"""
        self.server.register_endpoint("click_element", self.click_element)
        self.server.register_endpoint("enter_text", self.enter_text)
        self.server.register_endpoint("capture_screen", self.capture_screen)
        # Additional endpoints
        
    def click_element(self, selector):
        """Click UI element identified by selector"""
        # Implement UI Automation to click element
        
    def enter_text(self, text, target=None):
        """Type text in the specified target"""
        # Implement text entry logic
        
    def capture_screen(self, region=None):
        """Capture screen or region for context"""
        # Implement screen capture
```

### 6.3 Security Considerations

- User confirmation for sensitive operations
- Tiered permission levels for different actions
- Audit logging of desktop control actions
- Capability to restrict domains of operation

## 7. Knowledge System

### 7.1 Knowledge Graph (Long-term Memory)

- Stores structured relationships between entities
- Maintains persistent user preferences and history
- Maps domains to capabilities for agent routing
- Preserves context across multiple sessions
- Implemented using Neo4j or similar graph database

```python
# Example knowledge graph operations
def store_entity_relationship(entity1, relationship, entity2):
    query = f"""
    MERGE (a:{entity1.type} {{name: '{entity1.name}'}})
    MERGE (b:{entity2.type} {{name: '{entity2.name}'}})
    MERGE (a)-[r:{relationship}]->(b)
    RETURN a, r, b
    """
    knowledge_graph.execute(query)
```

### 7.2 Vector Database (Short-term Memory)

- Stores recent conversations and context in vector form
- Enables semantic search for relevant information
- Optimized for quick retrieval of similar content
- Automatically prunes older entries based on relevance and age
- Implemented using Milvus, Chroma, or similar vector database

```python
# Example vector database operations
def store_context_embedding(text, embedding, metadata=None):
    vector_db.insert(
        collection="context",
        vectors=[embedding],
        metadata=[metadata or {}],
        ids=[str(uuid.uuid4())]
    )
```

### 7.3 Memory Integration

The dual memory system works in concert, with the vector database providing quick access to recent context while the knowledge graph maintains long-term structured information:

```python
def retrieve_relevant_context(query, embedding):
    # First check vector database for recent similar context
    recent_contexts = vector_db.search(
        collection="context",
        query_vector=embedding,
        limit=5
    )
    
    # Then augment with structured knowledge from the graph
    knowledge_results = knowledge_graph.query(query)
    
    # Merge results with appropriate weighting
    return merge_context_results(recent_contexts, knowledge_results)
```

## 8. Technology Stack Recommendations

### 8.1 Core Framework

- **Microsoft AutoGen**: Provides robust multi-agent orchestration capabilities with built-in message routing and state management [Microsoft Research](https://www.microsoft.com/en-us/research/project/autogen/)
- **Python 3.10+**: Base language for the entire system

### 8.2 UI Components

- **Electron**: Cross-platform desktop application framework
- **React**: UI component library
- **Three.js**: 3D rendering for animated dot
- **Web Speech API**: Voice input/output in browser environment

### 8.3 Desktop Control

- **Windows UI Automation API**: Native Windows UI control
- **PyAutoGUI**: Cross-platform GUI automation
- **Microsoft UFO**: UI-Focused agent framework for Windows
- **Custom MCP Server implementation**: For standardized tool access

### 8.4 Knowledge Storage

- **Neo4j**: Graph database for knowledge graph implementation
- **Chroma DB**: Vector database optimized for LLM embeddings
- **Redis**: Optional caching layer for performance

### 8.5 Voice Processing

- **Porcupine**: Wake word detection
- **OpenAI Whisper**: Speech-to-text
- **ElevenLabs**: Text-to-speech with natural voice

### 8.6 Agent Communication

- **gRPC**: High-performance RPC framework for agent communication
- **Protocol Buffers**: Efficient serialization format
- **WebSockets**: Real-time communication with UI

### 8.7 Development Tools

- **Docker**: Containerization for consistent deployment
- **Poetry**: Python dependency management
- **GitHub Actions**: CI/CD pipeline
- **Pytest**: Testing framework

## 9. Implementation Strategy

### 9.1 Phased Approach

1. **Phase 1**: Implement PIA with basic UI and chat capabilities
2. **Phase 2**: Add CNC agent and initial domain agent framework
3. **Phase 3**: Implement voice interaction and desktop context awareness
4. **Phase 4**: Add desktop control capabilities via MCP servers
5. **Phase 5**: Integrate knowledge graph and vector database
6. **Phase 6**: Add specialized domain agents and enhance capabilities

### 9.2 Development Best Practices

- Use modular architecture with clear interfaces between components
- Implement comprehensive logging for debugging and audit purposes
- Create thorough test suites for each component
- Document all APIs and interfaces
- Establish clear security boundaries and permission models
- Use feature flags to control gradual rollout of capabilities

### 9.3 Evaluation Metrics

- Task completion success rate
- User satisfaction ratings
- Response latency
- Context retention accuracy
- Knowledge retrieval precision
- Desktop control success rate

## 10. Future Extensions

- **Multimodal Understanding**: Enhanced image and video understanding
- **Collaborative Workflows**: Multiple users working with the same agent system
- **Advanced Personalization**: Learning user preferences and adapting behavior
- **Cross-Device Synchronization**: Consistent experience across user devices
- **Third-Party API Integration**: Expanding capabilities through external services
- **Custom Domain Agent Development Kit**: Enabling users to create specialized agents

## 11. Conclusion

The "exo" multi-agent framework represents a new paradigm in human-computer interaction, combining minimalist interface design with powerful agent-based capabilities. By structuring the system around specialized agents coordinated through a hierarchical framework, "exo" can tackle complex tasks while presenting a simple, intuitive interface to users.

The system's ability to control the desktop environment directly, combined with its knowledge storage capabilities and voice interaction, creates a seamless experience that extends beyond traditional chatbot interactions. The initial specialized agents focused on software engineering and MCP server creation establish a foundation that can be expanded to cover additional domains as the system evolves.