"""
Monitor de Procesos Semi-Simulado
Captura procesos reales del sistema y simula algoritmos de despacho
"""
import psutil
import random
import time
from typing import Dict, List, Any, Optional

from .Process import Process
from ..base_monitor import BaseMonitor


class ProcessMonitor(BaseMonitor):
    """
    Monitor de procesos semi-simulado que:
    1. Captura procesos reales del sistema
    2. Permite seleccionarlos y asignarles propiedades simuladas
    3. Ejecuta algoritmos de despacho (FIFO, SJF, Round Robin)
    """
    
    def __init__(self, update_interval: float = 1.0):
        """
        Inicializa el monitor de procesos
        
        Args:
            update_interval: Intervalo en segundos entre actualizaciones
        """
        super().__init__(update_interval)
        self.real_processes: List[Dict[str, Any]] = []
        self.selected_processes: List[Process] = []
        self.simulation_results: Dict[str, Any] = {}
        self.quantum: int = 2  # Para Round Robin (default)
        
        # Caché para optimizar llamadas a psutil
        self._process_cache: List[Dict[str, Any]] = []
        self._cache_timestamp: float = 0
        self._cache_ttl: float = 2.0  # TTL de 2 segundos
        
    def collect_data(self) -> Dict[str, Any]:
        """
        Recolecta procesos reales del sistema
        
        Returns:
            Dict con procesos reales y resultados de simulación
        """
        self.real_processes = self._get_real_processes()
        
        return {
            'real_processes': self.real_processes,
            'selected_processes': [p.to_dict() for p in self.selected_processes],
            'simulation_results': self.simulation_results
        }
    
    def _get_real_processes(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de procesos reales del sistema con caché
        
        Returns:
            Lista de diccionarios con información de procesos
        """
        import time
        
        # Verificar si el caché es válido
        if time.time() - self._cache_timestamp < self._cache_ttl and self._process_cache:
            return self._process_cache
        
        # Caché inválido o vacío, obtener procesos nuevamente
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': round(pinfo['cpu_percent'] or 0, 2),
                    'memory_percent': round(pinfo['memory_percent'] or 0, 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Ordenar por nombre para mejor visualización
        processes.sort(key=lambda x: x['name'].lower())
        
        # Actualizar caché
        self._process_cache = processes
        self._cache_timestamp = time.time()
        
        return processes
    
    def add_process_from_real(self, pid: int, name: str, burst_time: Optional[int] = None) -> Process:
        """
        Agrega un proceso real a la lista de procesos seleccionados
        
        Args:
            pid: PID del proceso real
            name: Nombre del proceso
            burst_time: Tiempo de ráfaga (si es None, se genera aleatorio entre 5-15)
            
        Returns:
            El proceso agregado
            
        Raises:
            ValueError: Si los parámetros son inválidos o el proceso ya existe
        """
        # Validación de entrada
        if pid <= 0:
            raise ValueError(f"PID inválido: {pid}. Debe ser un número positivo")
        
        if not name or not isinstance(name, str) or name.strip() == "":
            raise ValueError("El nombre del proceso no puede estar vacío")
        
        if burst_time is not None:
            if not isinstance(burst_time, int) or burst_time < 1 or burst_time > 100:
                raise ValueError(f"Burst time inválido: {burst_time}. Debe estar entre 1 y 100")
        
        # Prevenir duplicados
        if any(p.pid == pid for p in self.selected_processes):
            raise ValueError(f"El proceso con PID {pid} ({name}) ya está seleccionado")
        
        # Generar burst time aleatorio si no se proporciona
        if burst_time is None:
            burst_time = random.randint(5, 15)
        
        arrival_time = time.time()
        
        process = Process(
            pid=pid,
            name=name.strip(),
            arrival_time=arrival_time,
            burst_time=burst_time
        )
        
        self.selected_processes.append(process)
        return process
    
    def clear_selected_processes(self):
        """Limpia la lista de procesos seleccionados"""
        self.selected_processes.clear()
        self.simulation_results.clear()
    
    def set_quantum(self, quantum: int):
        """
        Establece el quantum para Round Robin
        
        Args:
            quantum: Valor del quantum (tiempo por proceso)
        """
        if quantum > 0:
            self.quantum = quantum
    
    # ==================== ALGORITMOS DE PLANIFICACIÓN ====================
    
    def run_fifo(self) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo FIFO (First Come First Served)
        Los procesos se ejecutan en el orden exacto de llegada
        
        Returns:
            Dict con resultados y estadísticas
        """
        if not self.selected_processes:
            return {'error': 'No hay procesos seleccionados'}
        
        # Ordenar por tiempo de llegada
        processes = sorted(self.selected_processes, key=lambda p: p.arrival_time)
        
        current_time = 0
        execution_order = []
        
        for process in processes:
            # Si el proceso llega después del tiempo actual, avanzamos el tiempo
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            # Tiempo de inicio
            process.start_time = int(current_time)
            
            # El proceso se ejecuta completamente
            current_time += process.burst_time
            
            # Tiempo de finalización (Tf)
            process.completion_time = int(current_time)
            
            # Tiempo de retorno (Tr) = Tf - Tll
            process.turnaround_time = int(process.completion_time - process.arrival_time)
            
            # Tiempo de espera (Te) = Tr - Ts (según fórmula académica)
            process.waiting_time = process.turnaround_time - process.burst_time
            
            execution_order.append({
                'name': process.name,
                'pid': process.pid,
                'start': process.start_time,
                'end': process.completion_time,
                'burst': process.burst_time
            })
        
        # Calcular promedios y métricas
        avg_waiting = sum(p.waiting_time for p in processes) / len(processes)
        avg_turnaround = sum(p.turnaround_time for p in processes) / len(processes)
        avg_response = sum(p.start_time - p.arrival_time for p in processes) / len(processes)
        
        # Throughput: procesos completados por unidad de tiempo
        throughput = len(processes) / current_time if current_time > 0 else 0
        
        # CPU Utilization: porcentaje de tiempo que la CPU estuvo ocupada
        total_burst = sum(p.burst_time for p in processes)
        cpu_utilization = (total_burst / current_time * 100) if current_time > 0 else 0
        
        results = {
            'algorithm': 'FIFO',
            'processes': [p.to_dict() for p in processes],
            'execution_order': execution_order,
            'statistics': {
                'avg_waiting_time': round(avg_waiting, 1),
                'avg_turnaround_time': round(avg_turnaround, 1),
                'avg_response_time': round(avg_response, 1),
                'throughput': round(throughput, 1),
                'cpu_utilization': round(cpu_utilization, 1),
                'total_time': int(current_time)
            }
        }
        
        self.simulation_results = results
        return results
    
    def run_sjf(self) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo SJF Non-Preemptive (Shortest Job First)
        Los procesos se ejecutan por orden de ráfaga más corta,
        considerando los tiempos de llegada dinámicamente
        
        Returns:
            Dict con resultados y estadísticas
        """
        if not self.selected_processes:
            return {'error': 'No hay procesos seleccionados'}
        
        # Crear copias para no modificar los originales
        processes = [Process(p.pid, p.name, p.arrival_time, p.burst_time) 
                    for p in self.selected_processes]
        
        # Ordenar por tiempo de llegada inicialmente
        processes.sort(key=lambda p: p.arrival_time)
        
        current_time = 0
        execution_order = []
        completed_processes = []
        ready_queue = []
        
        # SJF dinámico: considera llegadas en tiempo real
        while processes or ready_queue:
            # Agregar todos los procesos que ya llegaron a la cola de listos
            while processes and processes[0].arrival_time <= current_time:
                ready_queue.append(processes.pop(0))
            
            if ready_queue:
                # Ejecutar el proceso con menor burst time
                ready_queue.sort(key=lambda p: (p.burst_time, p.arrival_time))
                process = ready_queue.pop(0)
                
                # Tiempo de inicio
                process.start_time = int(current_time)
                
                # El proceso se ejecuta completamente
                current_time += process.burst_time
                
                # Tiempo de finalización (Tf)
                process.completion_time = int(current_time)
                
                # Tiempo de retorno (Tr) = Tf - Tll
                process.turnaround_time = int(process.completion_time - process.arrival_time)
                
                # Tiempo de espera (Te) = Tr - Ts (según fórmula académica)
                process.waiting_time = process.turnaround_time - process.burst_time
                
                execution_order.append({
                    'name': process.name,
                    'pid': process.pid,
                    'start': process.start_time,
                    'end': process.completion_time,
                    'burst': process.burst_time
                })
                
                completed_processes.append(process)
            else:
                # Si la cola está vacía, saltar al próximo arrival
                if processes:
                    current_time = processes[0].arrival_time
        
        # Calcular promedios y métricas
        avg_waiting = sum(p.waiting_time for p in completed_processes) / len(completed_processes)
        avg_turnaround = sum(p.turnaround_time for p in completed_processes) / len(completed_processes)
        avg_response = sum(p.start_time - p.arrival_time for p in completed_processes) / len(completed_processes)
        
        # Throughput: procesos completados por unidad de tiempo
        throughput = len(completed_processes) / current_time if current_time > 0 else 0
        
        # CPU Utilization: porcentaje de tiempo que la CPU estuvo ocupada
        total_burst = sum(p.burst_time for p in completed_processes)
        cpu_utilization = (total_burst / current_time * 100) if current_time > 0 else 0
        
        results = {
            'algorithm': 'SJF',
            'processes': [p.to_dict() for p in completed_processes],
            'execution_order': execution_order,
            'statistics': {
                'avg_waiting_time': round(avg_waiting, 1),
                'avg_turnaround_time': round(avg_turnaround, 1),
                'avg_response_time': round(avg_response, 1),
                'throughput': round(throughput, 1),
                'cpu_utilization': round(cpu_utilization, 1),
                'total_time': int(current_time)
            }
        }
        
        self.simulation_results = results
        return results
    
    def run_round_robin(self, quantum: Optional[int] = None) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo Round Robin
        Cada proceso usa la CPU solo durante el quantum y vuelve a la cola
        
        Args:
            quantum: Tiempo del quantum (usa self.quantum si es None)
            
        Returns:
            Dict con resultados y estadísticas
        """
        if not self.selected_processes:
            return {'error': 'No hay procesos seleccionados'}
        
        if quantum is not None:
            self.quantum = quantum
        
        # Crear copias para no modificar los originales
        processes = [Process(p.pid, p.name, p.arrival_time, p.burst_time) 
                    for p in self.selected_processes]
        
        # Ordenar por tiempo de llegada para la cola inicial
        processes.sort(key=lambda p: p.arrival_time)
        
        current_time = 0
        queue = processes.copy()
        execution_order = []
        completed_processes = []
        
        while queue:
            process = queue.pop(0)
            
            # Si el proceso llega después del tiempo actual
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            # Primera vez que se ejecuta el proceso
            if process.start_time is None:
                process.start_time = current_time
            
            # Determinar cuánto tiempo se ejecuta
            execution_time = min(self.quantum, process.remaining_time)
            
            # Registrar la ejecución
            execution_order.append({
                'name': process.name,
                'pid': process.pid,
                'start': current_time,
                'end': current_time + execution_time,
                'burst': execution_time,
                'remaining': process.remaining_time - execution_time
            })
            
            # Actualizar tiempo y proceso
            current_time += execution_time
            process.remaining_time -= execution_time
            
            # Si el proceso terminó
            if process.remaining_time == 0:
                process.completion_time = current_time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                completed_processes.append(process)
            else:
                # El proceso vuelve a la cola
                queue.append(process)
        
        # Calcular promedios
        avg_waiting = sum(p.waiting_time for p in completed_processes) / len(completed_processes)
        avg_turnaround = sum(p.turnaround_time for p in completed_processes) / len(completed_processes)
        
        # Calcular métricas adicionales
        avg_response = sum(p.start_time - p.arrival_time for p in completed_processes) / len(completed_processes)
        
        # Throughput: procesos completados por unidad de tiempo
        throughput = len(completed_processes) / current_time if current_time > 0 else 0
        
        # CPU Utilization: porcentaje de tiempo que la CPU estuvo ocupada
        total_burst = sum(p.burst_time for p in completed_processes)
        cpu_utilization = (total_burst / current_time * 100) if current_time > 0 else 0
        
        results = {
            'algorithm': 'Round Robin',
            'quantum': self.quantum,
            'processes': [p.to_dict() for p in completed_processes],
            'execution_order': execution_order,
            'statistics': {
                'avg_waiting_time': round(avg_waiting, 1),
                'avg_turnaround_time': round(avg_turnaround, 1),
                'avg_response_time': round(avg_response, 1),
                'throughput': round(throughput, 1),
                'cpu_utilization': round(cpu_utilization, 1),
                'total_time': int(current_time),
                'context_switches': len(execution_order) - 1
            }
        }
        
        self.simulation_results = results
        return results
    
    def get_statistics_comparison(self) -> Dict[str, Any]:
        """
        Ejecuta los 3 algoritmos y compara sus estadísticas
        
        Returns:
            Dict con comparación de los 3 algoritmos
        """
        if not self.selected_processes:
            return {'error': 'No hay procesos seleccionados'}
        
        fifo_results = self.run_fifo()
        sjf_results = self.run_sjf()
        rr_results = self.run_round_robin()
        
        return {
            'comparison': {
                'FIFO': fifo_results['statistics'],
                'SJF': sjf_results['statistics'],
                'Round Robin': rr_results['statistics']
            },
            'details': {
                'FIFO': fifo_results,
                'SJF': sjf_results,
                'Round Robin': rr_results
            }
        }
