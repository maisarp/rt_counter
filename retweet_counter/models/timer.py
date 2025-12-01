from datetime import datetime
from typing import Optional

class Timer:
    def __init__(self, auto_start_count: int = 1, auto_stop_count: int = 50):
        """
        Initialize the Timer class.
        
        Args:
            auto_start_count (int): Count value that triggers automatic start (default: 1)
            auto_stop_count (int): Count value that triggers automatic stop (default: 50)
        """
        self.start_time: Optional[datetime] = None
        self.stop_time: Optional[datetime] = None
        self.is_running: bool = False
        self.auto_start_count = auto_start_count
        self.auto_stop_count = auto_stop_count
        self.elapsed_time: float = 0.0

    def start(self, manual: bool = True) -> None:
        """
        Start the timer.
        
        Args:
            manual (bool): Indicates if the start was triggered manually (default: True)
        """
        if not self.is_running:
            self.start_time = datetime.now()
            self.is_running = True

    def stop(self, manual: bool = True) -> float:
        """
        Stop the timer and return elapsed time in seconds.
        
        Args:
            manual (bool): Indicates if the stop was triggered manually (default: True)
            
        Returns:
            float: Elapsed time in seconds
        """
        if self.is_running:
            self.stop_time = datetime.now()
            self.is_running = False
            self.elapsed_time = (self.stop_time - self.start_time).total_seconds()
            return self.elapsed_time
        return self.elapsed_time

    def check_auto_trigger(self, count: int) -> None:
        """
        Check if the counter value should trigger automatic start/stop.
        
        Args:
            count (int): Current counter value
        """
        if count == self.auto_start_count:
            self.start(manual=False)
        elif count == self.auto_stop_count:
            self.stop(manual=False)
        elif count > self.auto_stop_count and count % self.auto_stop_count == 1:
            self.start(manual=False)
        elif count > self.auto_stop_count and count % self.auto_stop_count == 0:
            self.stop(manual=False)

    def get_elapsed_time(self) -> float:
        """
        Get the current elapsed time in seconds.
        
        Returns:
            float: Elapsed time in seconds
        """
        if self.is_running:
            current_time = datetime.now()
            return (current_time - self.start_time).total_seconds()
        return self.elapsed_time

    def reset(self) -> None:
        """Reset the timer to initial state."""
        self.start_time = None
        self.stop_time = None
        self.is_running = False
        self.elapsed_time = 0.0

    def configure_auto_triggers(self, start_count: int, stop_count: int) -> None:
        """
        Configure automatic start/stop trigger values.
        
        Args:
            start_count (int): New value for auto start trigger
            stop_count (int): New value for auto stop trigger
        """
        self.auto_start_count = start_count
        self.auto_stop_count = stop_count