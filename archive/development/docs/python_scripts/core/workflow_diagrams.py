#!/usr/bin/env python3
"""
Workflow Diagrams
================

Mermaid diagrams for visualizing the DevPost automation workflow architecture.
"""


def create_langgraph_workflow_diagram():
    """Create Mermaid diagram for the LangGraph workflow"""

    diagram = """
```mermaid
graph TD
    A[Browser Connection] --> B[Session Recovery]
    
    B --> C{Confidence Level}
    C -->|Low < 0.1| D[Ghostbusters Mode]
    C -->|Very Low 0.1-0.2| E[Ghostbusters Autonomous]
    C -->|Moderate 0.2-0.4| F[Prompt Mode]
    C -->|Low 0.3-0.4| G[Cautious Mode]
    C -->|High > 0.4| H[Page Detection]
    
    D --> I[Interactive Recovery]
    E --> J[Ghostbusters Consultation]
    F --> K[User Input Required]
    G --> H
    H --> L[Form Analysis]
    
    I --> M[Memory Qualification]
    J --> F
    K --> N{User Decision}
    N -->|Call Ghostbusters| J
    N -->|Proceed Cautiously| H
    N -->|Reset| O[Fresh Start]
    
    L --> P[Form Population]
    P --> Q[Form Submission]
    Q --> R[Navigation]
    R --> S[Validation]
    S --> T[Completion]
    
    M --> H
    O --> H
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#ffebee
    style E fill:#ffebee
    style F fill:#e8f5e8
    style G fill:#fff8e1
    style H fill:#e3f2fd
```
"""
    return diagram


def create_investigation_modules_diagram():
    """Create Mermaid diagram for the investigation modules"""

    diagram = """
```mermaid
graph TD
    A[Ghostbusters Consultation] --> B[Investigation Orchestrator]
    
    B --> C[Page Structure Analyzer]
    B --> D[Navigation Analyzer]
    B --> E[Content Analyzer]
    B --> F[Diagnostic Tester]
    
    C --> G[URL Pattern Analysis]
    C --> H[Title Analysis]
    C --> I[Form Element Counting]
    C --> J[Structure Classification]
    
    D --> K[Button Type Analysis]
    D --> L[Text Content Analysis]
    D --> M[Href Pattern Analysis]
    D --> N[Interaction Pattern Detection]
    
    E --> O[Key Phrase Extraction]
    E --> P[Content Type Classification]
    E --> Q[Language Pattern Detection]
    E --> R[Semantic Analysis]
    
    F --> S[Page Accessibility Test]
    F --> T[Navigation Presence Test]
    F --> U[Form Detection Test]
    F --> V[Content Analysis Test]
    
    G --> W[Investigation Results]
    H --> W
    I --> W
    J --> W
    K --> W
    L --> W
    M --> W
    N --> W
    O --> W
    P --> W
    Q --> W
    R --> W
    S --> W
    T --> W
    U --> W
    V --> W
    
    W --> X[Recommendation Generator]
    X --> Y[Risk Assessment]
    X --> Z[Strategy Determination]
    
    style A fill:#ffebee
    style B fill:#e8f5e8
    style C fill:#e3f2fd
    style D fill:#f3e5f5
    style E fill:#fff3e0
    style F fill:#e0f2f1
    style W fill:#fce4ec
    style X fill:#f1f8e9
```
"""
    return diagram


def create_confidence_routing_diagram():
    """Create Mermaid diagram for confidence-based routing"""

    diagram = """
```mermaid
graph TD
    A[Session Recovery Analysis] --> B[Multi-Dimensional Context Analysis]
    
    B --> C{Overall Confidence}
    
    C -->|Confidence < 0.1| D[Ghostbusters Mode]
    C -->|Confidence 0.1-0.2| E[Ghostbusters Autonomous]
    C -->|Confidence 0.2-0.4| F[Prompt Mode]
    C -->|Confidence 0.3-0.4| G[Cautious Mode]
    C -->|Confidence > 0.4| H[Autonomous Mode]
    
    D --> I["🚨 Interactive Recovery<br/>Completely confused<br/>Needs human help"]
    E --> J["🚨 Autonomous Investigation<br/>Too risky for human<br/>Ghostbusters deploy"]
    F --> K["🎖️ Tactical Discussion<br/>This is it! The moment<br/>we should have trained for!"]
    G --> L["⚠️ Cautious Navigation<br/>Proceed with caution<br/>Enhanced monitoring"]
    H --> M["✅ Autonomous Navigation<br/>High confidence<br/>Standard operation"]
    
    I --> N[User Input Required]
    J --> O[Autonomous Investigation]
    K --> P[User Decision Required]
    L --> Q[Page Detection]
    M --> Q
    
    N --> R[Recovery Options]
    O --> S[Return to Prompt Mode]
    P --> T{User Choice}
    
    R --> U[Memory Qualification]
    S --> V[Consensus Decision]
    T -->|Call Ghostbusters| J
    T -->|Proceed| Q
    T -->|Reset| W[Fresh Start]
    
    U --> Q
    V --> Q
    W --> Q
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#ffebee
    style E fill:#ffebee
    style F fill:#e8f5e8
    style G fill:#fff8e1
    style H fill:#e3f2fd
    style I fill:#ffcdd2
    style J fill:#ffcdd2
    style K fill:#c8e6c9
    style L fill:#fff9c4
    style M fill:#bbdefb
```
"""
    return diagram


def create_memory_management_diagram():
    """Create Mermaid diagram for tiered memory management"""

    diagram = """
```mermaid
graph TD
    A[Memory Manager] --> B[Short-Term Memory]
    A --> C[Long-Term Memory]
    A --> D[Memory Qualification Queue]
    
    B --> E[Session Data]
    B --> F[User Actions]
    B --> G[Current Page State]
    B --> H[Recovery State]
    
    C --> I[Persistent Patterns]
    C --> J[User Preferences]
    C --> K[Site-Specific Data]
    C --> L[Historical Analysis]
    
    D --> M[Pending Items]
    M --> N[User Qualification Required]
    N --> O{User Decision}
    
    O -->|Persist| P[Move to Long-Term]
    O -->|Discard| Q[Remove from Queue]
    O -->|Transform| R[Modify Data]
    
    P --> C
    Q --> S[Delete Item]
    R --> T[Apply Transformations]
    T --> P
    
    U[Session Save] --> V[Save All Memory]
    V --> W[Short-Term Memory]
    V --> X[Long-Term Memory]
    V --> Y[Qualification Queue]
    
    Z[Session Load] --> AA[Restore Memory State]
    AA --> B
    AA --> C
    AA --> D
    
    style A fill:#e8f5e8
    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style D fill:#fff3e0
    style U fill:#e0f2f1
    style Z fill:#fce4ec
```
"""
    return diagram


def create_prompt_mode_flow_diagram():
    """Create Mermaid diagram for Prompt Mode flow"""

    diagram = """
```mermaid
graph TD
    A[Prompt Mode Activated] --> B["🎖️ Military-Derived Exclamation<br/>This is it! The moment we should have trained for!"]
    
    B --> C[Situation Briefing]
    C --> D[Confidence Level: 0.35]
    C --> E[Similarity Type: unknown]
    C --> F[Current Page Analysis]
    
    D --> G[Tactical Discussion Points]
    E --> G
    F --> G
    
    G --> H[User Input Required]
    H --> I{User Response}
    
    I -->|Discuss Situation| J[Continue Tactical Discussion]
    I -->|Call Ghostbusters| K[Deploy Ghostbusters Consultation]
    I -->|Proceed Cautiously| L[Activate Cautious Navigation]
    I -->|Reset Fresh| M[Reset to Known State]
    I -->|Other| N[Clarify Intent]
    
    J --> O[Enhanced Analysis]
    O --> P[User Decision Required]
    
    K --> Q[Ghostbusters Investigation]
    Q --> R[Return with Findings]
    R --> S[Consensus Decision Required]
    
    L --> T[Page Detection with Caution]
    M --> U[Fresh Page Detection]
    N --> V[Request Clarification]
    
    P --> W{User Decision}
    S --> X{Consensus Decision}
    
    W -->|Proceed| T
    W -->|Call Ghostbusters| K
    W -->|Reset| U
    
    X -->|Follow Recommendation| Y[Execute Ghostbusters Strategy]
    X -->|Different Approach| Z[User-Provided Strategy]
    
    T --> AA[Navigation Success]
    U --> AA
    Y --> AA
    Z --> AA
    
    style A fill:#e8f5e8
    style B fill:#fff3e0
    style C fill:#e3f2fd
    style G fill:#f3e5f5
    style H fill:#ffebee
    style K fill:#ffcdd2
    style Q fill:#ffcdd2
    style S fill:#c8e6c9
    style AA fill:#bbdefb
```
"""
    return diagram


def create_rmddd_architecture_diagram():
    """Create Mermaid diagram showing RMDDD architecture"""

    diagram = """
```mermaid
graph TD
    A[LangGraph Workflow] --> B[Session Recovery Node]
    A --> C[Prompt Mode Node]
    A --> D[Ghostbusters Consultation Node]
    A --> E[Interactive Recovery Node]
    
    B --> F[Multi-Dimensional Context Analyzer]
    F --> G[Page Similarity Analyzer]
    F --> H[Confidence Calculator]
    
    C --> I[Prompt Mode Manager]
    I --> J[Conversation Handler]
    I --> K[Decision Router]
    
    D --> L[Investigation Orchestrator]
    L --> M[Page Structure Analyzer]
    L --> N[Navigation Analyzer]
    L --> O[Content Analyzer]
    L --> P[Diagnostic Tester]
    
    E --> Q[Tiered Memory Manager]
    Q --> R[Short-Term Memory]
    Q --> S[Long-Term Memory]
    Q --> T[Memory Qualification Queue]
    
    M --> U[URL Pattern Analysis]
    M --> V[Title Analysis]
    M --> W[Form Element Counting]
    
    N --> X[Button Type Analysis]
    N --> Y[Text Content Analysis]
    N --> Z[Interaction Patterns]
    
    O --> AA[Key Phrase Extraction]
    O --> BB[Content Classification]
    O --> CC[Language Patterns]
    
    P --> DD[Accessibility Tests]
    P --> EE[Navigation Tests]
    P --> FF[Form Detection Tests]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#ffebee
    style E fill:#fff3e0
    style L fill:#e0f2f1
    style Q fill:#fce4ec
```
"""
    return diagram


def generate_all_diagrams():
    """Generate all Mermaid diagrams"""

    diagrams = {
        "langgraph_workflow": create_langgraph_workflow_diagram(),
        "investigation_modules": create_investigation_modules_diagram(),
        "confidence_routing": create_confidence_routing_diagram(),
        "memory_management": create_memory_management_diagram(),
        "prompt_mode_flow": create_prompt_mode_flow_diagram(),
        "rmddd_architecture": create_rmddd_architecture_diagram(),
    }

    return diagrams


if __name__ == "__main__":
    diagrams = generate_all_diagrams()

    for name, diagram in diagrams.items():
        print(f"\n{'='*60}")
        print(f"DIAGRAM: {name.upper().replace('_', ' ')}")
        print(f"{'='*60}")
        print(diagram)
