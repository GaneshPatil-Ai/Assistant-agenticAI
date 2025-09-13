from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER_INPUT = "user_input"
    SUPERVISOR_QUESTION = "supervisor_question"
    WORKER_RESPONSE = "worker_response"
    SUPERVISOR_DECISION = "supervisor_decision"
    WORKER_TASK = "worker_task"

class Message(BaseModel):
    content: str
    sender: str
    message_type: MessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class SupervisorMemory(BaseModel):
    conversation_history: List[Message] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    context_gathered: Dict[str, Any] = Field(default_factory=dict)
    decision_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_message(self, message: Message):
        self.conversation_history.append(message)
        # Keep only recent messages based on memory size
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_recent_context(self, limit: int = 5) -> List[Message]:
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def update_context(self, key: str, value: Any):
        self.context_gathered[key] = value

class WorkerState(BaseModel):
    worker_id: str
    current_task: Optional[str] = None
    task_result: Optional[str] = None
    is_busy: bool = False
    last_activity: datetime = Field(default_factory=datetime.now)

class SystemState(BaseModel):
    supervisor_memory: SupervisorMemory = Field(default_factory=SupervisorMemory)
    worker_states: Dict[str, WorkerState] = Field(default_factory=dict)
    current_phase: str = "gathering_info"  # gathering_info, processing, completed
    user_query: Optional[str] = None
    final_response: Optional[str] = None
    error_message: Optional[str] = None