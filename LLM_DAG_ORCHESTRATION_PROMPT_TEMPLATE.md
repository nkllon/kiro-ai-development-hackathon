# LLM Prompt Template for DAG Orchestrated Parallel Execution

## 🎯 **OPTIMAL PROMPT STRUCTURE**

### **Basic Prompt Template**

```
You have access to a DAG Orchestrated Parallel Execution System that can execute complex workflows with intelligent dependency management and parallel optimization.

SYSTEM CAPABILITIES:
- Mathematical DAG validation (prevents circular dependencies)
- Intelligent parallel task scheduling with multiple strategies
- Real-time monitoring and progress tracking
- Automatic resource management and optimization
- Failure isolation and recovery
- AI-powered learning and optimization suggestions

USAGE PATTERN:
1. Define tasks with clear dependencies
2. Validate execution plan before running
3. Execute with appropriate configuration
4. Monitor results and optimize

Please help me [SPECIFIC REQUEST] using this DAG orchestration system.

CONTEXT: [Provide specific workflow details, constraints, and requirements]
```

---

## 🚀 **SCENARIO-SPECIFIC PROMPTS**

### **1. Complex Workflow Orchestration**

```
I need to orchestrate a complex workflow using the DAG Orchestrated Parallel Execution System.

WORKFLOW REQUIREMENTS:
- [List specific tasks and their relationships]
- [Performance requirements: speed, reliability, resource constraints]
- [Dependencies between tasks]
- [Error handling requirements]

SYSTEM AVAILABLE:
- DAG validation with cycle detection
- Parallel execution with resource management
- Multiple scheduling strategies (ADAPTIVE, CRITICAL_PATH, PRIORITY, etc.)
- Real-time monitoring and progress tracking
- Failure isolation and recovery

Please:
1. Design the optimal task structure with dependencies
2. Recommend the best execution and scheduling strategies
3. Implement the workflow with proper error handling
4. Include validation and monitoring

CONSTRAINTS: [Specify any limitations or requirements]
```

### **2. Performance Optimization**

```
I have a workflow that needs performance optimization using the DAG Orchestration System.

CURRENT SITUATION:
- [Describe existing workflow]
- [Current performance metrics]
- [Bottlenecks or issues]

OPTIMIZATION GOALS:
- [Speed, resource efficiency, reliability, etc.]

AVAILABLE TOOLS:
- Adaptive scheduling with critical path analysis
- Resource-aware parallel execution
- AI learning for pattern optimization
- Dynamic concurrency adjustment
- Performance monitoring and analytics

Please analyze and optimize this workflow using the DAG orchestration capabilities.
```

### **3. System Integration**

```
I need to integrate existing systems/processes into the DAG Orchestrated Parallel Execution framework.

EXISTING SYSTEMS:
- [List current systems, APIs, processes]
- [Current integration points]
- [Data flow and dependencies]

INTEGRATION REQUIREMENTS:
- [Reliability, monitoring, error handling needs]
- [Performance requirements]
- [Compatibility constraints]

DAG SYSTEM FEATURES:
- ReflectiveModule integration for observability
- ACE Reporter for real-time progress broadcasting
- AI Memory Palace for learning and optimization
- Comprehensive error handling and recovery
- Infrastructure validation and prefire testing

Please design the integration strategy and implementation.
```

---

## 🎨 **PROMPT CUSTOMIZATION GUIDE**

### **Key Elements to Include**

1. **Clear Objective**: What you want to accomplish
2. **Context**: Specific workflow, systems, or requirements
3. **Constraints**: Performance, resource, or technical limitations
4. **System Capabilities**: Reference relevant DAG orchestration features
5. **Expected Output**: Code, configuration, analysis, or recommendations

### **System Capabilities to Mention**

Choose relevant capabilities based on your use case:

- **Mathematical DAG Validation**: For complex dependency management
- **Parallel Execution**: For performance-critical workflows
- **Intelligent Scheduling**: For optimization scenarios
- **Real-time Monitoring**: For operational visibility
- **Failure Isolation**: For reliability requirements
- **AI Learning**: For continuous improvement
- **Resource Management**: For efficient resource utilization
- **Integration Components**: For system connectivity

---

## 📋 **EXAMPLE PROMPTS BY USE CASE**

### **Data Pipeline Orchestration**

```
I need to build a data processing pipeline using the DAG Orchestrated Parallel Execution System.

PIPELINE REQUIREMENTS:
- Extract data from multiple sources (APIs, databases, files)
- Transform data with validation and cleaning
- Load into target systems with error handling
- Process 10GB+ datasets efficiently
- Handle failures gracefully without data loss

DAG SYSTEM STRENGTHS:
- Parallel execution for independent data sources
- Dependency management for transform/load sequences
- Resource-aware scheduling for large datasets
- Failure isolation to prevent cascade failures
- Real-time monitoring for pipeline visibility

Please design and implement this data pipeline with optimal performance and reliability.
```

### **CI/CD Workflow Automation**

```
I want to optimize our CI/CD pipeline using DAG Orchestrated Parallel Execution.

CURRENT PIPELINE:
- Code checkout and validation
- Multiple test suites (unit, integration, e2e)
- Build artifacts for different platforms
- Security scanning and compliance checks
- Deployment to staging and production

OPTIMIZATION GOALS:
- Reduce total pipeline time from 45 minutes to under 20 minutes
- Improve reliability and error recovery
- Better resource utilization
- Real-time progress visibility

DAG ORCHESTRATION BENEFITS:
- Parallel execution of independent test suites
- Intelligent scheduling based on resource requirements
- Failure isolation to continue other tasks
- Critical path optimization for fastest completion
- Comprehensive monitoring and reporting

Please redesign this CI/CD pipeline for optimal performance.
```

### **Machine Learning Workflow**

```
I need to orchestrate a machine learning training and deployment workflow.

ML WORKFLOW STAGES:
- Data preprocessing and feature engineering
- Model training with hyperparameter tuning
- Model validation and testing
- Model deployment and monitoring
- Batch inference processing

REQUIREMENTS:
- Handle large datasets (100GB+)
- Parallel hyperparameter experiments
- Resource-intensive GPU training
- Automated model validation
- Rollback capability for failed deployments

DAG SYSTEM CAPABILITIES:
- Resource-aware scheduling for GPU allocation
- Parallel execution for hyperparameter experiments
- Dependency management for training pipelines
- AI Memory Palace for learning optimal configurations
- Comprehensive error handling and recovery

Please design this ML workflow with the DAG orchestration system.
```

---

## 🔧 **ADVANCED PROMPT TECHNIQUES**

### **Multi-Step Prompting**

```
STEP 1: Analyze my workflow requirements and recommend the optimal DAG structure
STEP 2: Design the task definitions with proper dependencies
STEP 3: Configure the orchestration settings for best performance
STEP 4: Implement error handling and monitoring
STEP 5: Provide optimization recommendations based on AI learning capabilities

WORKFLOW DETAILS: [Your specific requirements]
```

### **Iterative Optimization**

```
I have an existing DAG workflow that needs optimization. Please:

1. ANALYZE: Review the current implementation for bottlenecks
2. OPTIMIZE: Suggest improvements using DAG orchestration features
3. IMPLEMENT: Provide updated code with optimizations
4. VALIDATE: Include monitoring and validation strategies
5. LEARN: Leverage AI Memory Palace for continuous improvement

CURRENT WORKFLOW: [Provide existing implementation]
PERFORMANCE METRICS: [Current performance data]
OPTIMIZATION GOALS: [Specific targets]
```

### **Problem-Solution Format**

```
PROBLEM: [Describe specific challenge]
- Current approach and limitations
- Performance or reliability issues
- Resource constraints or requirements

SOLUTION REQUIREMENTS:
- Must use DAG Orchestrated Parallel Execution System
- Leverage [specific capabilities like parallel execution, AI learning, etc.]
- Meet [specific performance/reliability targets]

EXPECTED DELIVERABLES:
- Task definitions with dependencies
- Orchestration configuration
- Error handling strategy
- Monitoring and optimization plan

Please provide a comprehensive solution using the DAG orchestration capabilities.
```

---

## 🎯 **PROMPT OPTIMIZATION TIPS**

### **DO:**
- Be specific about your workflow requirements
- Mention relevant DAG system capabilities
- Include performance or reliability constraints
- Ask for complete implementations with error handling
- Request monitoring and optimization strategies

### **DON'T:**
- Use vague or generic requests
- Ignore dependency relationships
- Skip error handling requirements
- Forget about monitoring and observability
- Overlook resource management needs

### **BEST PRACTICES:**
- Start with validation before execution
- Include both success and failure scenarios
- Ask for configuration recommendations
- Request performance optimization suggestions
- Include integration with existing systems

---

## 📚 **REFERENCE MATERIALS TO MENTION**

When prompting, you can reference:
- `DAG_ORCHESTRATION_OPERATING_INSTRUCTIONS.md` for detailed usage
- `DAG_ORCHESTRATION_QUICK_REFERENCE.md` for syntax and examples
- `demo_dag_orchestration_system.py` for working examples
- System capabilities: mathematical validation, parallel execution, AI learning

---

## 🚀 **READY-TO-USE PROMPT**

```
I need help with [SPECIFIC WORKFLOW/TASK] using the DAG Orchestrated Parallel Execution System.

REQUIREMENTS:
- [List specific requirements]
- [Performance/reliability needs]
- [Resource constraints]

SYSTEM CAPABILITIES AVAILABLE:
- Mathematical DAG validation with cycle detection
- Intelligent parallel execution with resource management
- Multiple scheduling strategies (Adaptive, Critical Path, Priority)
- Real-time monitoring and progress tracking
- Failure isolation and recovery mechanisms
- AI-powered learning and optimization
- Integration with ACE Reporter and AI Memory Palace

Please provide:
1. Optimal task structure with dependencies
2. Configuration recommendations
3. Complete implementation with error handling
4. Monitoring and optimization strategy

CONTEXT: [Provide specific details about your use case]
```

This prompt template ensures LLMs understand the full capabilities of the DAG Orchestration System and can provide optimal solutions! 🎯