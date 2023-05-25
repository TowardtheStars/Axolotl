
from concurrent import futures
import logging
from typing import Any, List, TypeVar


logger = logging.getLogger(__name__)

class TaskManager:
    INSTANCE = None
    def __init__(self) -> None:
        self.__thread_pool = futures.ThreadPoolExecutor(1, thread_name_prefix='Task')

    @property
    def thread_pool(self) -> futures.ThreadPoolExecutor:
        return self.__thread_pool
    
    def cancel_all(self):
        self.thread_pool.shutdown(wait=False, cancel_futures=True)

task_manager = None
def getTaskManager() -> TaskManager:
    global task_manager
    if not task_manager:
        task_manager = TaskManager()
    return task_manager

T = TypeVar('T')
class Task:
    def __init__(self, name = '') -> None:
        self._thread: futures.Future = None

    def get_thread(self) -> futures.Future:
        return self._thread
    
    def start(self):
        self.on_start()
        self._thread = getTaskManager().thread_pool.submit(self.run)
        futures.as_completed([self._thread])
        
    def is_running(self) -> bool:
        return self._thread.running()

    def on_start(self):
        pass

    def run(self) -> T:
        pass

    def cancel(self) -> bool:
        return self._thread.cancel()
    
    def get_name(self) -> str:
        return ''
    

class TaskList:
    def __init__(self) -> None:
        self.tasks: List[Task] = []
        
