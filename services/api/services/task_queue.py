import asyncio
from typing import Dict, Any
from collections import deque
import logging

logger = logging.getLogger(__name__)

class TaskQueue:
    def __init__(self):
        self.queue = deque()
        self.processing = {}
        self.retry_counts = {}
        self.max_retries = 3

    async def enqueue_task(self, task_id: str, task_data: Dict[str, Any]):
        self.queue.append((task_id, task_data))
        logger.info(f"Task {task_id} enqueued")

    async def process_next_task(self):
        if not self.queue:
            return None
        
        task_id, task_data = self.queue.popleft()
        self.processing[task_id] = task_data
        return task_id, task_data

    async def mark_completed(self, task_id: str):
        if task_id in self.processing:
            del self.processing[task_id]
            if task_id in self.retry_counts:
                del self.retry_counts[task_id]

    async def retry_task(self, task_id: str) -> bool:
        if task_id not in self.retry_counts:
            self.retry_counts[task_id] = 0
        
        if self.retry_counts[task_id] >= self.max_retries:
            return False
        
        self.retry_counts[task_id] += 1
        if task_id in self.processing:
            task_data = self.processing[task_id]
            await self.enqueue_task(task_id, task_data)
            return True
        return False

task_queue = TaskQueue()

async def distribute_task(task_request: Dict[str, Any], target_node_id: str) -> Dict[str, Any]:
    try:
        task_id = f"task_{len(task_queue.queue)}"
        await task_queue.enqueue_task(task_id, {
            "request": task_request,
            "target_node": target_node_id
        })
        return {"task_id": task_id, "status": "enqueued"}
    except Exception as e:
        logger.error(f"Error distributing task: {str(e)}")
        raise

async def task_retry(task_id: str) -> Dict[str, Any]:
    success = await task_queue.retry_task(task_id)
    if not success:
        raise ValueError(f"Task {task_id} exceeded retry limit or not found")
    return {"status": "retrying"}

def validate_task_parameters(task_name: str, parameters: Dict[str, Any]) -> bool:
    # Add parameter validation logic here
    return True
