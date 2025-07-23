# Agent Protocol Implementation - Subtask 12.4

## Overview

This document describes the implementation of the **div99 Agent Protocol** for enhanced agent communication in our multi-agent revenue optimization system. This implementation completes **Subtask 12.4: Enhanced Agent Communication Protocols** by providing industry-standard REST API endpoints for agent interaction.

## Agent Protocol Features

### 🔌 div99 Agent Protocol Compliance
- **REST API Standard**: Full compliance with div99 Agent Protocol specification
- **OpenAPI Documentation**: Auto-generated API docs at `/ap/v1/docs`
- **Task-Step Model**: Hierarchical task execution with detailed step tracking
- **Artifact Management**: File and data artifact handling
- **Status Tracking**: Real-time task and step status monitoring

### 🤖 Multi-Agent Integration
- **Lead Intelligence Agent**: DeepSeek LLM for customer pattern analysis
- **Revenue Optimization Agent**: Llama3 LLM for business strategy
- **Intelligent Routing**: Automatic task routing based on content analysis
- **Collaborative Execution**: Multi-agent workflows for complex tasks

### 🏢 Hong Kong Telecom Specialization
- **Three HK Focus**: Specialized for Hong Kong telecommunications market
- **Customer Segmentation**: Premium, Family, Business, Budget, Tourist segments
- **Revenue Optimization**: Pricing strategy, retention offers, upsell opportunities
- **Market Compliance**: GDPR/PDPO privacy compliance built-in

## API Endpoints

### Core Agent Protocol Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ap/v1/agent/tasks` | List all tasks |
| `POST` | `/ap/v1/agent/tasks` | Create a new task |
| `GET` | `/ap/v1/agent/tasks/{task_id}` | Get specific task |
| `POST` | `/ap/v1/agent/tasks/{task_id}/steps` | Create a step for a task |
| `GET` | `/ap/v1/agent/tasks/{task_id}/steps` | List steps for a task |
| `GET` | `/ap/v1/agent/tasks/{task_id}/steps/{step_id}` | Get specific step |

### Health and Status Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ap/v1/agent/health` | Health check and system status |
| `GET` | `/ap/v1/docs` | Interactive API documentation |
| `GET` | `/ap/v1/redoc` | Alternative API documentation |

## Task Types and Routing

### 1. Lead Intelligence Tasks
**Trigger Keywords**: customer, data, pattern, churn, lead, segment, analyze

**Capabilities**:
- Customer behavior pattern analysis
- Lead quality scoring (1-10 scale)
- Churn risk prediction
- Market trend identification
- Customer segmentation

**Example Request**:
```json
{
  "input": "Analyze customer patterns and identify high-value leads for Hong Kong telecom market",
  "additional_input": {
    "focus": "lead_intelligence",
    "market": "hong_kong_telecom",
    "priority": "high"
  }
}
```

### 2. Revenue Optimization Tasks
**Trigger Keywords**: pricing, offer, strategy, retention, revenue, optimize

**Capabilities**:
- Three HK product matching
- Pricing strategy optimization
- Retention offer development
- Competitive positioning analysis
- Revenue maximization tactics

**Example Request**:
```json
{
  "input": "Develop pricing strategy and retention offers for premium customers",
  "additional_input": {
    "focus": "revenue_optimization",
    "customer_segment": "premium_individual",
    "priority": "high"
  }
}
```

### 3. Collaborative Tasks
**Default for complex or mixed requests**

**Capabilities**:
- Multi-agent collaboration
- Comprehensive analysis combining both agents
- Task delegation between agents
- Unified recommendations

**Example Request**:
```json
{
  "input": "Perform comprehensive customer analysis and develop integrated revenue strategy",
  "additional_input": {
    "focus": "collaborative",
    "agents": ["lead_intelligence", "revenue_optimization"],
    "priority": "high"
  }
}
```

## Installation and Setup

### 1. Dependencies
```bash
pip install fastapi>=0.110.0 uvicorn>=0.29.0
pip install -r requirements.txt
```

### 2. Environment Variables
Ensure you have the required API keys in your environment:
```bash
export OPENROUTER_API_KEY="your_openrouter_api_key"
export DEEPSEEK_API_KEY="your_deepseek_api_key"  # Optional if using OpenRouter
```

### 3. Start the Server
```bash
# Method 1: Direct execution
python src/agents/agent_protocol.py --host 127.0.0.1 --port 8080

# Method 2: Demo script
python demo_agent_protocol_server.py
```

### 4. Verify Installation
```bash
# Health check
curl http://127.0.0.1:8080/ap/v1/agent/health

# View API documentation
open http://127.0.0.1:8080/ap/v1/docs
```

## Usage Examples

### Creating a Lead Intelligence Task

```bash
curl -X POST http://127.0.0.1:8080/ap/v1/agent/tasks \\
  -H "Content-Type: application/json" \\
  -d '{
    "input": "Analyze customer churn patterns for Hong Kong telecom customers",
    "additional_input": {
      "focus": "lead_intelligence",
      "analysis_type": "churn_prediction"
    }
  }'
```

**Expected Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "input": "Analyze customer churn patterns for Hong Kong telecom customers",
  "status": "created",
  "created_at": "2025-07-23T10:30:00Z",
  "modified_at": "2025-07-23T10:30:00Z"
}
```

### Getting Task Status

```bash
curl http://127.0.0.1:8080/ap/v1/agent/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Expected Response** (after execution):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "input": "Analyze customer churn patterns for Hong Kong telecom customers",
  "status": "completed",
  "artifacts": [
    {
      "artifact_id": "result_001",
      "file_name": "churn_analysis.json",
      "relative_path": "results/churn_analysis.json"
    }
  ],
  "created_at": "2025-07-23T10:30:00Z",
  "modified_at": "2025-07-23T10:32:15Z"
}
```

### Creating and Monitoring Steps

```bash
# Create a step
curl -X POST http://127.0.0.1:8080/ap/v1/agent/tasks/550e8400-e29b-41d4-a716-446655440000/steps \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Customer Segmentation Analysis",
    "additional_input": {
      "segment_focus": "premium_customers"
    }
  }'

# List all steps for the task
curl http://127.0.0.1:8080/ap/v1/agent/tasks/550e8400-e29b-41d4-a716-446655440000/steps
```

## Architecture Integration

### Multi-Agent System Integration
```python
from src.agents.agent_protocol import create_agent_protocol_server
from src.agents.multi_agent_system import MultiAgentRevenueSystem

# Create integrated system
multi_agent_system = MultiAgentRevenueSystem()
agent_protocol_server = create_agent_protocol_server(multi_agent_system)

# Start server
agent_protocol_server.start_server(host="127.0.0.1", port=8080)
```

### Custom Agent Integration
The Agent Protocol server automatically integrates with:
- **Lead Intelligence Agent** (`src/agents/lead_intelligence_agent.py`)
- **Revenue Optimization Agent** (`src/agents/revenue_optimization_agent.py`)
- **Privacy Pipeline** for data protection
- **OpenRouter Client** for LLM access

## Testing

### Unit Tests
```bash
python test_agent_protocol.py
```

### Integration Tests
```bash
# Start server in background
python src/agents/agent_protocol.py --host 127.0.0.1 --port 8080 &

# Run integration tests
python -m pytest tests/test_agent_protocol_integration.py
```

### Manual Testing
```bash
# Interactive API testing
open http://127.0.0.1:8080/ap/v1/docs

# Command line testing
python demo_agent_protocol_server.py
```

## Implementation Details

### Task Status Flow
```
created → running → completed/failed
```

### Step Status Flow
```
created → running → completed/failed
```

### Agent Routing Logic
1. **Explicit Routing**: Check `additional_input.focus` field
2. **Content Analysis**: Analyze task input for keywords
3. **Default Routing**: Route to collaborative multi-agent workflow

### Error Handling
- **HTTP 404**: Task or step not found
- **HTTP 500**: Internal server error
- **HTTP 422**: Invalid input validation
- **Graceful Degradation**: Fallback to simulated responses if agents fail

## Performance Considerations

### Asynchronous Execution
- All task execution is asynchronous using Python `asyncio`
- Non-blocking API responses
- Background task processing

### Resource Management
- Task result caching
- Automatic cleanup of completed tasks
- Memory-efficient artifact storage

### Scalability
- Stateless API design
- Horizontal scaling ready
- Database persistence option (future enhancement)

## Security

### Authentication (Future Enhancement)
- API key authentication
- JWT token support
- Rate limiting

### Data Privacy
- Automatic data pseudonymization
- GDPR/PDPO compliance
- Encrypted artifact storage

## Monitoring and Logging

### Health Monitoring
```bash
curl http://127.0.0.1:8080/ap/v1/agent/health
```

**Response**:
```json
{
  "status": "healthy",
  "agent_protocol_version": "1.0.0",
  "multi_agent_system": "ready",
  "active_tasks": 5,
  "timestamp": "2025-07-23T10:30:00Z"
}
```

### Logging
- Comprehensive logging via Python `logging` module
- Agent execution logs
- API request/response logs
- Error tracking and debugging

## Future Enhancements

### Planned Features
1. **Persistent Storage**: Database backend for task persistence
2. **WebSocket Support**: Real-time task status updates
3. **Authentication**: API key and OAuth2 support
4. **Rate Limiting**: Request throttling and quotas
5. **Metrics**: Prometheus metrics integration
6. **Agent Discovery**: Dynamic agent registration
7. **Workflow Engine**: Complex multi-step workflows

### Integration Opportunities
1. **Zapier Integration**: Workflow automation
2. **Slack/Teams Bots**: Conversational interfaces
3. **CRM Systems**: Direct customer data integration
4. **BI Tools**: Analytics dashboard integration

## Troubleshooting

### Common Issues

**Server Won't Start**:
```bash
# Check port availability
netstat -an | findstr :8080

# Check dependencies
pip list | grep fastapi
pip list | grep uvicorn
```

**Agent Not Responding**:
```bash
# Check OpenRouter API key
echo $OPENROUTER_API_KEY

# Check health endpoint
curl http://127.0.0.1:8080/ap/v1/agent/health
```

**Tasks Stuck in 'running' Status**:
- Check agent logs for errors
- Verify LLM API connectivity
- Restart server if necessary

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Start server with debug
python src/agents/agent_protocol.py --host 127.0.0.1 --port 8080 --debug
```

## Conclusion

The div99 Agent Protocol implementation provides a robust, industry-standard interface for our multi-agent revenue optimization system. It enables:

- **Standardized Communication**: Industry-standard REST API
- **Enhanced Collaboration**: Seamless multi-agent workflows
- **Easy Integration**: Simple API for external systems
- **Scalable Architecture**: Ready for production deployment
- **Hong Kong Telecom Focus**: Specialized for Three HK market

This implementation successfully completes **Subtask 12.4: Enhanced Agent Communication Protocols** and positions our multi-agent system for enterprise deployment and integration with external tools and platforms.

---

**Next Steps**: 
- Complete Task 12 Multi-Agent Architecture
- Deploy to production environment
- Integrate with customer CRM systems
- Develop monitoring dashboards
