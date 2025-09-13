# LangGraph Supervisor-Worker System

A sophisticated multi-agent system built with LangGraph that implements a supervisor node with historic memory and stateless worker nodes. The system can gather sufficient information before involving worker agents and asks follow-up questions when needed.

## 🏗️ Architecture

### Core Components

1. **Supervisor Node** - The central coordinator with historic memory
   - Analyzes user queries and determines if sufficient information is available
   - Generates follow-up questions when information is missing
   - Creates execution plans and coordinates worker tasks
   - Maintains conversation history and context
   - Synthesizes worker results into coherent responses

2. **Worker Nodes** - Stateless specialized agents
   - **Research Worker**: Handles information gathering, data analysis, and fact-checking
   - **Creative Worker**: Manages content generation, creative writing, and artistic tasks

3. **LangGraph Workflow** - Orchestrates the entire system
   - Conditional routing based on information sufficiency
   - State management and memory persistence
   - Asynchronous task execution

### System Flow

```
User Query → Supervisor Analysis → [Info Sufficient?]
    ↓                              ↓
[No] → Generate Follow-up Questions → User Response → New Query
    ↓
[Yes] → Create Execution Plan → Coordinate Workers → Synthesize Results → Final Response
```

## 🚀 Features

- **Intelligent Information Gathering**: Supervisor analyzes queries and asks targeted follow-up questions
- **Historic Memory**: Maintains conversation context and user preferences
- **Dynamic Worker Coordination**: Automatically assigns tasks to appropriate workers
- **Stateless Workers**: Workers can be scaled independently without state concerns
- **RESTful API**: Built with Falcon framework for easy integration
- **Production Ready**: Gunicorn deployment with proper async support
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd langgraph-supervisor-worker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4)
- `SUPERVISOR_MEMORY_SIZE`: Number of conversation messages to retain (default: 10)
- `WORKER_TIMEOUT`: Worker task timeout in seconds (default: 30)

### Gunicorn Configuration

The `gunicorn.conf.py` file is optimized for production deployment with:
- 4 worker processes
- Async support via Uvicorn workers
- Proper timeout and connection settings
- Comprehensive logging

## 🚀 Running the Application

### Development Mode

```bash
python run.py
```

### Production Mode with Gunicorn

```bash
gunicorn -c gunicorn.conf.py api:app
```

### Docker (if available)

```bash
docker build -t langgraph-supervisor-worker .
docker run -p 8000:8000 --env-file .env langgraph-supervisor-worker
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Workflow Information
```http
GET /info
```

### Process Query
```http
POST /query
Content-Type: application/json

{
    "query": "Your query here"
}
```

### Follow-up Response
```http
POST /followup
Content-Type: application/json

{
    "response": "Additional information",
    "session_id": "optional_session_id"
}
```

## 🧪 Testing

Run the test client to verify the system:

```bash
python test_client.py
```

The test client demonstrates:
- Health check verification
- Workflow information retrieval
- Query processing with different complexity levels
- Follow-up question handling
- Worker coordination

## 📊 Example Usage

### Simple Query (Needs More Info)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Help me write something"}'
```

**Response**: The supervisor will ask follow-up questions about topic, audience, style, etc.

### Complex Query (Sufficient Info)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Research quantum computing developments and create a creative summary for beginners"}'
```

**Response**: The system will coordinate research and creative workers to produce a comprehensive response.

## 🔧 Customization

### Adding New Workers

1. Create a new worker class in `workers.py`
2. Implement the `process_task` method
3. Add to `WORKER_REGISTRY`
4. Update the supervisor's execution planning logic

### Modifying Supervisor Behavior

- Adjust the analysis prompts in `supervisor.py`
- Modify memory retention policies in `models.py`
- Update routing logic in `workflow.py`

### Extending the API

- Add new endpoints in `api.py`
- Implement additional middleware as needed
- Extend error handling for specific use cases

## 📈 Monitoring and Logging

The system provides comprehensive logging:
- Query processing logs
- Worker execution logs
- Error tracking
- Performance metrics

Logs are output to stdout/stderr for easy integration with log aggregation systems.

## 🚨 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is set in `.env`
   - Verify the key has sufficient credits

2. **Worker Timeout**
   - Increase `WORKER_TIMEOUT` in configuration
   - Check network connectivity to OpenAI

3. **Memory Issues**
   - Reduce `SUPERVISOR_MEMORY_SIZE` if needed
   - Monitor worker process memory usage

### Debug Mode

Enable debug logging by modifying the logging level in `api.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [LangChain](https://github.com/langchain-ai/langchain)
- Web framework: [Falcon](https://falconframework.org/)
- Production server: [Gunicorn](https://gunicorn.org/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub
4. Check the LangGraph documentation for LangGraph-specific questions
