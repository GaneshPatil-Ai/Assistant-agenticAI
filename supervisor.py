from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from models import SystemState, SupervisorMemory, Message, MessageType, WorkerState
from workers import WORKER_REGISTRY, execute_worker_task
from config import Config
import asyncio
import json

class Supervisor:
    """Supervisor node with historic memory that coordinates worker tasks"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model=Config.OPENAI_MODEL,
            temperature=0.3
        )
        self.memory = SupervisorMemory()
        
    async def analyze_user_query(self, user_query: str, state: SystemState) -> Dict[str, Any]:
        """Analyze user query and determine if more information is needed"""
        try:
            system_prompt = """You are a supervisor agent responsible for understanding user requests and determining the best course of action.
            
            Your responsibilities:
            1. Analyze the user's request
            2. Determine if you have enough information to proceed
            3. If information is missing, ask specific follow-up questions
            4. If you have enough information, plan the execution strategy
            
            Return your analysis as JSON with the following structure:
            {
                "has_sufficient_info": boolean,
                "missing_information": [list of missing details],
                "follow_up_questions": [list of specific questions],
                "execution_plan": {
                    "required_workers": [list of worker IDs],
                    "task_breakdown": [list of tasks],
                    "estimated_complexity": "low/medium/high"
                },
                "confidence_score": float (0-1)
            }"""
            
            # Get recent context from memory
            recent_context = state.supervisor_memory.get_recent_context()
            context_summary = "\n".join([f"{msg.sender}: {msg.content}" for msg in recent_context])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                User Query: {user_query}
                
                Recent Conversation Context:
                {context_summary}
                
                Current Gathered Information:
                {json.dumps(state.supervisor_memory.context_gathered, indent=2)}
                
                Available Workers: {list(WORKER_REGISTRY.keys())}
                
                Analyze this request and provide your assessment.
                """)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.content)
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "has_sufficient_info": False,
                    "missing_information": ["Unable to parse analysis"],
                    "follow_up_questions": ["Could you please rephrase your request?"],
                    "execution_plan": {"required_workers": [], "task_breakdown": [], "estimated_complexity": "unknown"},
                    "confidence_score": 0.0
                }
                
        except Exception as e:
            return {
                "has_sufficient_info": False,
                "missing_information": [f"Error in analysis: {str(e)}"],
                "follow_up_questions": ["There was an error processing your request. Please try again."],
                "execution_plan": {"required_workers": [], "task_breakdown": [], "estimated_complexity": "unknown"},
                "confidence_score": 0.0
            }
    
    async def generate_follow_up_questions(self, missing_info: List[str], user_query: str) -> List[str]:
        """Generate specific follow-up questions based on missing information"""
        try:
            system_prompt = """Generate 2-3 specific, clear follow-up questions to gather missing information.
            Make questions conversational and easy to understand."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                Original Query: {user_query}
                Missing Information: {', '.join(missing_info)}
                
                Generate follow-up questions to gather this missing information.
                """)
            ]
            
            response = await self.llm.ainvoke(messages)
            # Split response into individual questions
            questions = [q.strip() for q in response.content.split('\n') if q.strip() and '?' in q]
            return questions[:3]  # Limit to 3 questions
            
        except Exception as e:
            return [f"Could you provide more details about: {', '.join(missing_info)}"]
    
    async def create_execution_plan(self, user_query: str, analysis: Dict[str, Any], state: SystemState) -> Dict[str, Any]:
        """Create a detailed execution plan for the workers"""
        try:
            system_prompt = """Create a detailed execution plan for coordinating worker tasks.
            
            Return the plan as JSON with this structure:
            {
                "worker_assignments": [
                    {
                        "worker_id": "worker_name",
                        "task": "specific task description",
                        "priority": "high/medium/low",
                        "dependencies": ["list of tasks this depends on"]
                    }
                ],
                "execution_order": ["ordered list of task IDs"],
                "expected_outputs": ["list of expected results"],
                "quality_checks": ["list of validation steps"]
            }"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                User Query: {user_query}
                Analysis: {json.dumps(analysis, indent=2)}
                Available Workers: {list(WORKER_REGISTRY.keys())}
                
                Create a detailed execution plan.
                """)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            try:
                plan = json.loads(response.content)
                return plan
            except json.JSONDecodeError:
                # Fallback plan
                return {
                    "worker_assignments": [
                        {
                            "worker_id": "research_worker",
                            "task": "Gather information related to the query",
                            "priority": "high",
                            "dependencies": []
                        },
                        {
                            "worker_id": "creative_worker",
                            "task": "Process and present the information creatively",
                            "priority": "medium",
                            "dependencies": ["research_worker"]
                        }
                    ],
                    "execution_order": ["research_worker", "creative_worker"],
                    "expected_outputs": ["Research findings", "Creative presentation"],
                    "quality_checks": ["Verify information accuracy", "Ensure creative output meets requirements"]
                }
                
        except Exception as e:
            return {
                "worker_assignments": [],
                "execution_order": [],
                "expected_outputs": [],
                "quality_checks": []
            }
    
    async def coordinate_workers(self, execution_plan: Dict[str, Any], state: SystemState) -> Dict[str, Any]:
        """Coordinate the execution of worker tasks according to the plan"""
        try:
            results = {}
            worker_assignments = execution_plan.get("worker_assignments", [])
            
            for assignment in worker_assignments:
                worker_id = assignment["worker_id"]
                task = assignment["task"]
                
                # Check if worker is available
                if worker_id in state.worker_states and state.worker_states[worker_id].is_busy:
                    results[worker_id] = f"Worker {worker_id} is busy"
                    continue
                
                # Execute task
                try:
                    result = await execute_worker_task(worker_id, task, state.supervisor_memory.context_gathered)
                    results[worker_id] = result
                    
                    # Update worker state
                    if worker_id not in state.worker_states:
                        state.worker_states[worker_id] = WorkerState(worker_id=worker_id)
                    
                    state.worker_states[worker_id].current_task = task
                    state.worker_states[worker_id].task_result = result
                    state.worker_states[worker_id].is_busy = False
                    state.worker_states[worker_id].last_activity = state.worker_states[worker_id].last_activity
                    
                except Exception as e:
                    results[worker_id] = f"Error executing task: {str(e)}"
            
            return results
            
        except Exception as e:
            return {"error": f"Coordination error: {str(e)}"}
    
    async def synthesize_results(self, worker_results: Dict[str, Any], user_query: str, state: SystemState) -> str:
        """Synthesize worker results into a coherent final response"""
        try:
            system_prompt = """You are synthesizing the results from multiple workers into a coherent, 
            well-structured response for the user. Combine the information logically and ensure 
            the final response directly addresses the user's original query."""
            
            results_summary = "\n".join([f"{worker}: {result}" for worker, result in worker_results.items()])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                Original User Query: {user_query}
                
                Worker Results:
                {results_summary}
                
                Create a comprehensive, well-structured response that addresses the user's query.
                """)
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            return f"Error synthesizing results: {str(e)}"
    
    def update_memory(self, message: Message, state: SystemState):
        """Update supervisor memory with new information"""
        state.supervisor_memory.add_message(message)
        
        # Extract and store key information
        if message.message_type == MessageType.USER_INPUT:
            # Try to extract structured information from user input
            state.supervisor_memory.update_context("last_user_input", message.content)
        
        elif message.message_type == MessageType.WORKER_RESPONSE:
            # Store worker responses for context
            worker_id = message.sender
            state.supervisor_memory.update_context(f"worker_{worker_id}_last_response", message.content)