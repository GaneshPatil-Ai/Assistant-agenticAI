# 🚀 Quick Start Guide

Get the LangGraph Supervisor-Worker system running in 5 minutes!

## 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

## 3. Test the System

```bash
# Run the demo (no API needed)
python demo.py

# Or start the API server
python run.py

# In another terminal, test the API
python test_client.py
```

## 4. Production Deployment

```bash
# Using Gunicorn
gunicorn -c gunicorn.conf.py api:app

# Using Docker
docker build -t langgraph-supervisor-worker .
docker run -p 8000:8000 --env-file .env langgraph-supervisor-worker
```

## 5. API Usage

```bash
# Health check
curl http://localhost:8000/health

# Process a query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Research AI trends and create a summary"}'
```

## 🎯 What You Get

- **Supervisor Node**: Intelligent query analysis with follow-up questions
- **Research Worker**: Information gathering and analysis
- **Creative Worker**: Content generation and creative tasks
- **RESTful API**: Easy integration with your applications
- **Production Ready**: Gunicorn deployment with async support

## 🆘 Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Run `python demo.py` to see the system in action
- Use `python test_client.py` to test the API endpoints

Happy coding! 🎉