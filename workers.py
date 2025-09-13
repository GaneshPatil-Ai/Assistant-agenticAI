from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from models import SystemState, WorkerState, Message, MessageType
from config import Config
import asyncio

class ResearchWorker:
    """Worker responsible for gathering information and research tasks"""
    
    def __init__(self, worker_id: str = "research_worker"):
        self.worker_id = worker_id
        self.llm = ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model=Config.OPENAI_MODEL,
            temperature=0.1
        )
        
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> str:
        """Process research-related tasks"""
        try:
            system_prompt = """You are a research worker specialized in gathering and analyzing information. 
            Your task is to provide accurate, well-researched information based on the given task.
            Be thorough but concise in your response."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Task: {task}\nContext: {context or 'No additional context'}")
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            return f"Error in research worker: {str(e)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "capabilities": [
                "information_gathering",
                "data_analysis", 
                "fact_checking",
                "source_verification"
            ],
            "specialization": "research_and_analysis"
        }

class CreativeWorker:
    """Worker responsible for creative tasks and content generation"""
    
    def __init__(self, worker_id: str = "creative_worker"):
        self.worker_id = worker_id
        self.llm = ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model=Config.OPENAI_MODEL,
            temperature=0.7
        )
        
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> str:
        """Process creative tasks"""
        try:
            system_prompt = """You are a creative worker specialized in generating creative content, 
            writing, brainstorming, and artistic tasks. Your responses should be imaginative, 
            engaging, and tailored to the specific creative requirements."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Creative Task: {task}\nContext: {context or 'No additional context'}")
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            return f"Error in creative worker: {str(e)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "capabilities": [
                "content_generation",
                "creative_writing",
                "brainstorming",
                "artistic_creation",
                "storytelling"
            ],
            "specialization": "creativity_and_content"
        }

# Worker registry
WORKER_REGISTRY = {
    "research_worker": ResearchWorker(),
    "creative_worker": CreativeWorker()
}

async def execute_worker_task(worker_id: str, task: str, context: Dict[str, Any] = None) -> str:
    """Execute a task on a specific worker"""
    if worker_id not in WORKER_REGISTRY:
        return f"Worker {worker_id} not found"
    
    worker = WORKER_REGISTRY[worker_id]
    return await worker.process_task(task, context)