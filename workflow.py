from typing import Dict, Any, List
from langgraph import StateGraph, END
from langgraph.graph import START
from models import SystemState, Message, MessageType
from supervisor import Supervisor
from workers import WORKER_REGISTRY
import asyncio
import json

class LangGraphWorkflow:
    """Main workflow orchestrating supervisor and worker nodes"""
    
    def __init__(self):
        self.supervisor = Supervisor()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(SystemState)
        
        # Add nodes
        workflow.add_node("supervisor_analysis", self._supervisor_analysis_node)
        workflow.add_node("gather_info", self._gather_info_node)
        workflow.add_node("execute_workers", self._execute_workers_node)
        workflow.add_node("synthesize_results", self._synthesize_results_node)
        
        # Add edges
        workflow.add_edge(START, "supervisor_analysis")
        
        # Conditional routing based on supervisor analysis
        workflow.add_conditional_edges(
            "supervisor_analysis",
            self._route_after_analysis,
            {
                "gather_info": "gather_info",
                "execute_workers": "execute_workers",
                "end": END
            }
        )
        
        workflow.add_edge("gather_info", END)
        workflow.add_edge("execute_workers", "synthesize_results")
        workflow.add_edge("synthesize_results", END)
        
        return workflow.compile()
    
    async def _supervisor_analysis_node(self, state: SystemState) -> SystemState:
        """Supervisor analyzes the user query and determines next steps"""
        try:
            # Create user message and update memory
            user_message = Message(
                content=state.user_query,
                sender="user",
                message_type=MessageType.USER_INPUT
            )
            self.supervisor.update_memory(user_message, state)
            
            # Analyze the query
            analysis = await self.supervisor.analyze_user_query(state.user_query, state)
            
            # Store analysis in state
            state.supervisor_memory.update_context("last_analysis", analysis)
            
            # Update phase based on analysis
            if analysis.get("has_sufficient_info", False):
                state.current_phase = "processing"
            else:
                state.current_phase = "gathering_info"
            
            return state
            
        except Exception as e:
            state.error_message = f"Error in supervisor analysis: {str(e)}"
            return state
    
    async def _gather_info_node(self, state: SystemState) -> SystemState:
        """Generate follow-up questions to gather missing information"""
        try:
            analysis = state.supervisor_memory.context_gathered.get("last_analysis", {})
            missing_info = analysis.get("missing_information", [])
            
            if missing_info:
                follow_up_questions = await self.supervisor.generate_follow_up_questions(
                    missing_info, state.user_query
                )
                
                # Create supervisor question message
                question_message = Message(
                    content="\n".join(follow_up_questions),
                    sender="supervisor",
                    message_type=MessageType.SUPERVISOR_QUESTION
                )
                self.supervisor.update_memory(question_message, state)
                
                # Store questions for API response
                state.supervisor_memory.update_context("follow_up_questions", follow_up_questions)
            
            return state
            
        except Exception as e:
            state.error_message = f"Error in gathering info: {str(e)}"
            return state
    
    async def _execute_workers_node(self, state: SystemState) -> SystemState:
        """Execute worker tasks according to the execution plan"""
        try:
            analysis = state.supervisor_memory.context_gathered.get("last_analysis", {})
            
            # Create execution plan
            execution_plan = await self.supervisor.create_execution_plan(
                state.user_query, analysis, state
            )
            
            # Store plan in state
            state.supervisor_memory.update_context("execution_plan", execution_plan)
            
            # Execute workers
            worker_results = await self.supervisor.coordinate_workers(execution_plan, state)
            
            # Store results
            state.supervisor_memory.update_context("worker_results", worker_results)
            
            # Update phase
            state.current_phase = "completed"
            
            return state
            
        except Exception as e:
            state.error_message = f"Error in executing workers: {str(e)}"
            return state
    
    async def _synthesize_results_node(self, state: SystemState) -> SystemState:
        """Synthesize worker results into final response"""
        try:
            worker_results = state.supervisor_memory.context_gathered.get("worker_results", {})
            
            if worker_results:
                final_response = await self.supervisor.synthesize_results(
                    worker_results, state.user_query, state
                )
                
                state.final_response = final_response
                
                # Create final message
                final_message = Message(
                    content=final_response,
                    sender="supervisor",
                    message_type=MessageType.SUPERVISOR_DECISION
                )
                self.supervisor.update_memory(final_message, state)
            
            return state
            
        except Exception as e:
            state.error_message = f"Error in synthesizing results: {str(e)}"
            return state
    
    def _route_after_analysis(self, state: SystemState) -> str:
        """Route to next node based on supervisor analysis"""
        analysis = state.supervisor_memory.context_gathered.get("last_analysis", {})
        
        if state.error_message:
            return "end"
        
        if analysis.get("has_sufficient_info", False):
            return "execute_workers"
        else:
            return "gather_info"
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a user query through the workflow"""
        try:
            # Initialize state
            initial_state = SystemState(user_query=user_query)
            
            # Initialize worker states
            for worker_id in WORKER_REGISTRY.keys():
                initial_state.worker_states[worker_id] = WorkerState(worker_id=worker_id)
            
            # Execute workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            # Prepare response
            response = {
                "status": "success",
                "current_phase": final_state.current_phase,
                "supervisor_memory_size": len(final_state.supervisor_memory.conversation_history),
                "active_workers": len([w for w in final_state.worker_states.values() if w.is_busy])
            }
            
            if final_state.error_message:
                response["status"] = "error"
                response["error"] = final_state.error_message
            
            elif final_state.current_phase == "gathering_info":
                response["action"] = "gather_info"
                response["follow_up_questions"] = final_state.supervisor_memory.context_gathered.get("follow_up_questions", [])
                response["message"] = "Please provide additional information to proceed."
            
            elif final_state.current_phase == "completed":
                response["action"] = "completed"
                response["final_response"] = final_state.final_response
                response["worker_results"] = final_state.supervisor_memory.context_gathered.get("worker_results", {})
                response["message"] = "Task completed successfully."
            
            return response
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Workflow execution error: {str(e)}"
            }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the workflow and available workers"""
        return {
            "workflow_type": "supervisor_worker",
            "available_workers": {
                worker_id: worker.get_capabilities() 
                for worker_id, worker in WORKER_REGISTRY.items()
            },
            "supervisor_capabilities": [
                "query_analysis",
                "information_gathering",
                "worker_coordination",
                "result_synthesis"
            ],
            "memory_features": [
                "conversation_history",
                "context_tracking",
                "decision_history"
            ]
        }