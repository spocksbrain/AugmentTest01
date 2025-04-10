"""
Domain Agent base class implementation
"""

import logging
import uuid
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DomainAgent:
    """
    Base class for all domain agents.
    
    Domain agents are specialized agents that handle tasks in a specific domain.
    All domain agents must implement this interface to ensure compatibility with
    the Command & Control Agent.
    """
    
    def __init__(self, domain_name: str, capabilities: List[str]):
        """
        Initialize a domain agent.
        
        Args:
            domain_name: The domain name
            capabilities: List of capabilities this agent has
        """
        self.domain = domain_name
        self.capabilities = capabilities
        self.active_tasks = {}
        logger.info(f"Domain Agent initialized for domain: {domain_name}")
    
    def handle_task(self, task: str, context: Optional[Dict] = None) -> str:
        """
        Process a domain-specific task.
        
        Args:
            task: The task description
            context: Optional context information
            
        Returns:
            A task ID for tracking
        """
        logger.info(f"Handling task in {self.domain} domain: {task[:50]}...")
        
        # Generate a task ID if not provided in context
        task_id = context.get("subtask_id") if context else uuid.uuid4().hex
        
        # Store task information
        self.active_tasks[task_id] = {
            "task": task,
            "context": context,
            "status": "in_progress",
            "progress": 0,
            "result": None
        }
        
        # This method should be overridden by subclasses to implement
        # domain-specific logic. This base implementation just returns a placeholder.
        self._process_task(task_id)
        
        return task_id
    
    def _process_task(self, task_id: str) -> None:
        """
        Process a task. This method should be overridden by subclasses.
        
        Args:
            task_id: The task ID
        """
        # This is a placeholder implementation
        # Subclasses should override this method with domain-specific logic
        logger.warning(f"_process_task not implemented for {self.domain} domain")
        
        # Simulate task completion
        self.active_tasks[task_id]["status"] = "completed"
        self.active_tasks[task_id]["progress"] = 100
        self.active_tasks[task_id]["result"] = {
            "message": f"Task processed by {self.domain} agent (placeholder implementation)"
        }
    
    def report_progress(self, task_id: str, progress: int) -> None:
        """
        Update task progress.
        
        Args:
            task_id: The task ID
            progress: The progress percentage (0-100)
        """
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["progress"] = progress
            logger.info(f"Task {task_id} progress: {progress}%")
    
    def get_result(self, task_id: str) -> Dict:
        """
        Retrieve completed task result.
        
        Args:
            task_id: The task ID
            
        Returns:
            The task result
        """
        if task_id in self.active_tasks:
            return {
                "task_id": task_id,
                "status": self.active_tasks[task_id]["status"],
                "progress": self.active_tasks[task_id]["progress"],
                "result": self.active_tasks[task_id].get("result")
            }
        else:
            return {"error": f"Task {task_id} not found"}
    
    def handle_interruption(self, task_id: str) -> None:
        """
        Gracefully handle task interruption.
        
        Args:
            task_id: The task ID
        """
        if task_id in self.active_tasks:
            logger.info(f"Interrupting task {task_id}")
            self.active_tasks[task_id]["status"] = "interrupted"
            # Clean up resources - this should be implemented by subclasses
            # if they allocate specific resources for tasks
