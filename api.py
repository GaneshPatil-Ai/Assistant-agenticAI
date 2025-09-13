import falcon
import json
import asyncio
from typing import Dict, Any
from workflow import LangGraphWorkflow
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryProcessor:
    """Falcon resource for processing user queries"""
    
    def __init__(self):
        self.workflow = LangGraphWorkflow()
    
    async def on_post(self, req, resp):
        """Process a user query through the LangGraph workflow"""
        try:
            # Parse request body
            try:
                body = await req.get_media()
                user_query = body.get('query', '').strip()
            except Exception:
                # Fallback for older Falcon versions
                body = json.loads(req.bounded_stream.read().decode('utf-8'))
                user_query = body.get('query', '').strip()
            
            if not user_query:
                resp.status = falcon.HTTP_400
                resp.media = {
                    "error": "Query is required",
                    "status": "error"
                }
                return
            
            # Process query through workflow
            logger.info(f"Processing query: {user_query[:100]}...")
            result = await self.workflow.process_query(user_query)
            
            # Set response
            resp.status = falcon.HTTP_200
            resp.media = result
            
            logger.info(f"Query processed successfully. Status: {result.get('status')}")
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            resp.status = falcon.HTTP_500
            resp.media = {
                "error": f"Internal server error: {str(e)}",
                "status": "error"
            }

class WorkflowInfo:
    """Falcon resource for getting workflow information"""
    
    def __init__(self):
        self.workflow = LangGraphWorkflow()
    
    def on_get(self, req, resp):
        """Get information about the workflow and available workers"""
        try:
            info = self.workflow.get_workflow_info()
            resp.status = falcon.HTTP_200
            resp.media = info
        except Exception as e:
            logger.error(f"Error getting workflow info: {str(e)}")
            resp.status = falcon.HTTP_500
            resp.media = {
                "error": f"Internal server error: {str(e)}",
                "status": "error"
            }

class HealthCheck:
    """Falcon resource for health check"""
    
    def on_get(self, req, resp):
        """Simple health check endpoint"""
        resp.status = falcon.HTTP_200
        resp.media = {
            "status": "healthy",
            "service": "langgraph-supervisor-worker",
            "version": "1.0.0"
        }

class FollowUpHandler:
    """Falcon resource for handling follow-up responses"""
    
    def __init__(self):
        self.workflow = LangGraphWorkflow()
    
    async def on_post(self, req, resp):
        """Handle follow-up responses from users"""
        try:
            # Parse request body
            try:
                body = await req.get_media()
                follow_up_response = body.get('response', '').strip()
                session_id = body.get('session_id', '')
            except Exception:
                # Fallback for older Falcon versions
                body = json.loads(req.bounded_stream.read().decode('utf-8'))
                follow_up_response = body.get('response', '').strip()
                session_id = body.get('session_id', '')
            
            if not follow_up_response:
                resp.status = falcon.HTTP_400
                resp.media = {
                    "error": "Follow-up response is required",
                    "status": "error"
                }
                return
            
            # For now, we'll return a simple acknowledgment
            # In a full implementation, you'd want to integrate this with session management
            resp.status = falcon.HTTP_200
            resp.media = {
                "status": "success",
                "message": "Follow-up response received",
                "session_id": session_id,
                "next_action": "Please submit a new query with the additional information"
            }
            
        except Exception as e:
            logger.error(f"Error handling follow-up: {str(e)}")
            resp.status = falcon.HTTP_500
            resp.media = {
                "error": f"Internal server error: {str(e)}",
                "status": "error"
            }

# Create Falcon application
app = falcon.App()

# Add routes
app.add_route('/query', QueryProcessor())
app.add_route('/info', WorkflowInfo())
app.add_route('/health', HealthCheck())
app.add_route('/followup', FollowUpHandler())

# Add middleware for CORS and JSON handling
class CORSMiddleware:
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        resp.set_header('Access-Control-Allow-Headers', 'Content-Type')

app.add_middleware(CORSMiddleware())

# Error handlers
@app.add_error_handler(Exception)
def handle_exception(ex, req, resp, params):
    logger.error(f"Unhandled exception: {str(ex)}")
    resp.status = falcon.HTTP_500
    resp.media = {
        "error": "Internal server error",
        "status": "error"
    }

@app.add_error_handler(falcon.HTTPError)
def handle_http_error(ex, req, resp, params):
    resp.media = {
        "error": ex.description,
        "status": "error"
    }