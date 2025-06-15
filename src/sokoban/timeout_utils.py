import signal
import platform
import threading
import functools
from typing import Any, Callable, Optional

class TimeoutError(Exception):
    """自定义超时异常"""
    pass

def timeout_handler(func: Callable, timeout_duration: int) -> Any:
    """
    Cross-platform timeout handler that works on both Windows and Unix-like systems.
    
    Args:
        func: The function to execute
        timeout_duration: Timeout in seconds
        
    Returns:
        The result of the function if it completes within the timeout period
        
    Raises:
        TimeoutError: If the function execution exceeds the timeout period
    """
    result = []
    error = []
    
    def target():
        try:
            result.append(func())
        except Exception as e:
            error.append(e)
            
    thread = threading.Thread(target=target)
    thread.daemon = True
    
    thread.start()
    thread.join(timeout_duration)
    
    if thread.is_alive():
        thread.join(0)  # 清理线程
        raise TimeoutError(f"Function execution timed out after {timeout_duration} seconds")
        
    if error:
        raise error[0]
        
    if result:
        return result[0]
    
    raise TimeoutError("Function returned no result")

def timeout(seconds: int) -> Callable:
    """
    跨平台的超时装饰器
    
    Args:
        seconds: 超时秒数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 将参数打包到一个新函数中
            wrapped = lambda: func(*args, **kwargs)
            return timeout_handler(wrapped, seconds)
        return wrapper
    return decorator