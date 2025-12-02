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
        # Flag para indicar se o timer foi iniciado na sessao atual
        # Reseta quando o app reinicia para startar no primeiro +1
        self._session_started: bool = False

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
        
        O timer inicia automaticamente quando:
        - E o primeiro +1 da sessao (app foi aberto/reiniciado)
        - Ou quando atinge o auto_start_count (geralmente 1)
        - Ou quando ultrapassa o auto_stop_count e o modulo eh 1
        
        Args:
            count (int): Current counter value
        """
        # Se ainda nao iniciou nesta sessao e o timer nao esta rodando,
        # inicia no primeiro clique de +1 (quando count aumentou)
        if not self._session_started and not self.is_running:
            self._session_started = True
            self.start(manual=False)
            return
        
        # Logica original para auto-stop em lotes
        if count == self.auto_stop_count:
            self.stop(manual=False)
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
        # Reseta flag de sessao para permitir novo auto-start no proximo +1
        self._session_started = False

    def configure_auto_triggers(self, start_count: int, stop_count: int) -> None:
        """
        Configure automatic start/stop trigger values.
        
        Args:
            start_count (int): New value for auto start trigger
            stop_count (int): New value for auto stop trigger
        """
        self.auto_start_count = start_count
        self.auto_stop_count = stop_count