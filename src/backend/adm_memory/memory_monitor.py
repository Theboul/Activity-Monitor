"""
Monitor de Memoria Semi-Simulado
Captura procesos reales del sistema y coordina la simulación de asignación de memoria
"""
import psutil
import time
from typing import Dict, List, Any, Optional
from ..base_monitor import BaseMonitor
from .MemoryProcess import MemoryProcess
from .Partition import Partition
from .algorithm import MemoryAlgorithm, PartitionType
from .fixed_partition_manager import FixedPartitionManager
from .variable_partition_manager import VariablePartitionManager


class MemoryMonitor(BaseMonitor):
    """
    Monitor de memoria semi-simulado que:
    1. Captura procesos reales del sistema y su consumo de memoria
    2. Coordina la simulación con particiones fijas o variables
    3. Delega la asignación a los managers especializados
    """
    
    def __init__(self, update_interval: float = 2.0):
        """
        Inicializa el monitor de memoria
        
        Args:
            update_interval: Intervalo en segundos entre actualizaciones
        """
        super().__init__(update_interval)
        
        # Datos reales del sistema
        self.system_total_ram: int = 0
        self.system_available_ram: int = 0
        self.real_processes: List[Dict[str, Any]] = []
        
        # Configuración de simulación
        self.simulation_memory: int = 0
        self.partition_type: Optional[PartitionType] = None
        self.selected_processes: List[MemoryProcess] = []
        self.assignment_results: Dict[str, Any] = {}
        
        # Managers especializados
        self.fixed_manager = FixedPartitionManager()
        self.variable_manager = VariablePartitionManager()
        
        # Caché para optimizar llamadas a psutil
        self._process_cache: List[Dict[str, Any]] = []
        self._cache_timestamp: float = 0
        self._cache_ttl: float = 2.0
        
        # ID auto-incremental para particiones
        self._next_partition_id: int = 1
    
    # ==================== CAPTURA DE DATOS REALES ====================
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Recolecta información real del sistema (RAM y procesos)
        
        Returns:
            Dict con información de RAM, procesos reales y estado de simulación
        """
        # Obtener información de RAM del sistema
        mem = psutil.virtual_memory()
        self.system_total_ram = int(mem.total / (1024**2))
        self.system_available_ram = int(mem.available / (1024**2))
        
        # Obtener procesos reales
        self.real_processes = self._get_real_processes()
        
        return {
            'system_ram': {
                'total': self.system_total_ram,
                'available': self.system_available_ram,
                'used': self.system_total_ram - self.system_available_ram,
                'percent': mem.percent
            },
            'real_processes': self.real_processes,
            'selected_processes': [p.to_dict() for p in self.selected_processes],
            'partitions': [p.to_dict() for p in self._get_current_partitions()],
            'assignment_results': self.assignment_results
        }
    
    def _get_real_processes(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de procesos reales del sistema con su consumo de memoria
        
        Returns:
            Lista de diccionarios con información de procesos
        """
        # Verificar si el caché es válido
        if time.time() - self._cache_timestamp < self._cache_ttl and self._process_cache:
            return self._process_cache
        
        # Obtener procesos del sistema
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                pinfo = proc.info
                memory_mb = int(pinfo['memory_info'].rss / (1024**2))
                
                # Solo incluir procesos que usen al menos 1 MB
                if memory_mb >= 1:
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'memory_mb': memory_mb
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                pass
        
        # Ordenar por consumo de memoria (descendente)
        processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        
        # Actualizar caché
        self._process_cache = processes
        self._cache_timestamp = time.time()
        
        return processes
    
    # ==================== CONFIGURACIÓN DE SIMULACIÓN ====================
    
    def setup_fixed_partitions(self, total_memory: int, partition_size: int, num_partitions: int):
        """
        Configura el sistema con particiones fijas (todas del mismo tamaño)
        
        Args:
            total_memory: Memoria total a simular en MB
            partition_size: Tamaño de cada partición en MB
            num_partitions: Número de particiones a crear
        
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        if total_memory <= 0:
            raise ValueError(f"Memoria total inválida: {total_memory}. Debe ser mayor a 0 MB")
        
        if partition_size <= 0:
            raise ValueError(f"Tamaño de partición inválido: {partition_size}. Debe ser mayor a 0 MB")
        
        if num_partitions <= 0:
            raise ValueError(f"Número de particiones inválido: {num_partitions}. Debe ser mayor a 0")
        
        total_partitions = partition_size * num_partitions
        if total_partitions > total_memory:
            raise ValueError(
                f"El espacio requerido ({total_partitions} MB = {partition_size} MB x {num_partitions}) "
                f"excede la memoria total ({total_memory} MB)"
            )
        
        # Limpiar estado anterior
        self.selected_processes.clear()
        self.assignment_results.clear()
        
        # Configurar simulación
        self.simulation_memory = total_memory
        self.partition_type = PartitionType.FIXED
        
        # Configurar manager de particiones fijas
        self._next_partition_id = self.fixed_manager.setup(partition_size, num_partitions, self._next_partition_id)
        
        print(f"[OK] Particiones fijas: {num_partitions} particiones de {partition_size} MB, {total_memory} MB totales")
    
    def setup_variable_partitions(self, total_memory: int):
        """
        Configura el sistema con particiones variables
        
        Args:
            total_memory: Memoria total a simular en MB
        
        Raises:
            ValueError: Si el parámetro es inválido
        """
        if total_memory <= 0:
            raise ValueError(f"Memoria total inválida: {total_memory}. Debe ser mayor a 0 MB")
        
        # Limpiar estado anterior
        self.selected_processes.clear()
        self.assignment_results.clear()
        
        # Configurar simulación
        self.simulation_memory = total_memory
        self.partition_type = PartitionType.VARIABLE
        
        # Configurar manager de particiones variables
        self._next_partition_id = self.variable_manager.setup(total_memory, self._next_partition_id)
        
        print(f"[OK] Particiones variables: {total_memory} MB totales")
    
    # ==================== GESTIÓN DE PROCESOS ====================
    
    def add_process_from_real(self, pid: int, name: str, memory_size: Optional[int] = None) -> MemoryProcess:
        """
        Agrega un proceso real a la lista de procesos seleccionados
        
        Args:
            pid: PID del proceso real
            name: Nombre del proceso
            memory_size: Tamaño en MB (si es None, se captura del sistema)
        
        Returns:
            El proceso agregado
        
        Raises:
            ValueError: Si los parámetros son inválidos o el proceso ya existe
        """
        if pid <= 0:
            raise ValueError(f"PID inválido: {pid}")
        
        if not name or not isinstance(name, str) or name.strip() == "":
            raise ValueError("El nombre del proceso no puede estar vacío")
        
        # Prevenir duplicados
        if any(p.pid == pid for p in self.selected_processes):
            raise ValueError(f"El proceso con PID {pid} ({name}) ya está seleccionado")
        
        # Si no se proporciona tamaño, capturarlo del sistema
        if memory_size is None:
            try:
                proc = psutil.Process(pid)
                memory_size = int(proc.memory_info().rss / (1024**2))
                if memory_size < 1:
                    memory_size = 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                memory_size = 10  # 10 MB por defecto
        
        if memory_size <= 0:
            raise ValueError(f"Tamaño de memoria inválido: {memory_size}")
        
        # Crear proceso
        process = MemoryProcess(
            pid=pid,
            name=name.strip(),
            memory_size=memory_size
        )
        
        self.selected_processes.append(process)
        return process
    
    def clear_selected_processes(self):
        """Limpia la lista de procesos seleccionados y resetea asignaciones"""
        self.selected_processes.clear()
        self.assignment_results.clear()
        
        # Liberar todas las particiones según el tipo
        if self.partition_type == PartitionType.FIXED:
            self.fixed_manager.clear_assignments()
        elif self.partition_type == PartitionType.VARIABLE:
            self.variable_manager.clear_assignments()
    
    def get_process_by_pid(self, pid: int) -> Optional[MemoryProcess]:
        """Busca un proceso por su PID"""
        for process in self.selected_processes:
            if process.pid == pid:
                return process
        return None
    
    # ==================== ASIGNACIÓN PRINCIPAL ====================
    
    def assign_processes(self, algorithm: MemoryAlgorithm) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo de asignación seleccionado para todos los procesos
        
        Args:
            algorithm: Algoritmo a utilizar (FIRST_FIT o BEST_FIT)
        
        Returns:
            Dict con resultados de la asignación
        
        Raises:
            ValueError: Si no hay configuración o procesos seleccionados
        """
        if self.partition_type is None:
            raise ValueError("Configure primero el tipo de particionamiento")
        
        if not self.selected_processes:
            raise ValueError("No hay procesos seleccionados")
        
        # Limpiar asignaciones anteriores
        if self.partition_type == PartitionType.FIXED:
            self.fixed_manager.clear_assignments()
        else:
            self.variable_manager.clear_assignments()
        
        # Resetear procesos
        for process in self.selected_processes:
            process.unassign()
        
        # Asignar procesos usando el manager apropiado
        assigned = []
        failed = []
        
        for process in self.selected_processes:
            if self.partition_type == PartitionType.FIXED:
                # Particiones fijas solo soportan First Fit
                if algorithm == MemoryAlgorithm.BEST_FIT:
                    raise ValueError(
                        "Best Fit no está disponible para particiones fijas. "
                        "Use First Fit (todas las particiones tienen el mismo tamaño)"
                    )
                success = self.fixed_manager.assign_process(process)
            else:
                success = self.variable_manager.assign_process(process, algorithm)
            
            if success:
                assigned.append(process.to_dict())
            else:
                failed.append(process.to_dict())
        
        # Calcular estadísticas
        fragmentation = self.calculate_fragmentation()
        statistics = self.get_statistics()
        
        # Guardar resultados
        self.assignment_results = {
            'algorithm': algorithm.value,
            'partition_type': self.partition_type.value,
            'assigned_processes': assigned,
            'failed_processes': failed,
            'partitions': [p.to_dict() for p in self._get_current_partitions()],
            'fragmentation': fragmentation,
            'statistics': statistics
        }
        
        return self.assignment_results
    
    # ==================== UTILIDADES ====================
    
    def release_process(self, pid: int):
        """
        Libera un proceso de la memoria y termina el proceso real del sistema
        
        Args:
            pid: PID del proceso a liberar
        """
        process = self.get_process_by_pid(pid)
        if not process:
            raise ValueError(f"No se encontró el proceso con PID {pid}")
        
        if not process.is_assigned():
            raise ValueError(f"El proceso {process.name} no está asignado")
        
        # Liberar usando el manager apropiado
        if self.partition_type == PartitionType.FIXED:
            self.fixed_manager.release_process(process.partition_id)
        else:
            self.variable_manager.release_process(process.partition_id)
        
        # Eliminar el proceso de la lista de seleccionados
        self.selected_processes.remove(process)
        
        # Intentar cerrar el proceso real del sistema
        try:
            real_process = psutil.Process(pid)
            real_process.terminate()  # Enviar señal de terminación
            print(f"[OK] Proceso real {process.name} (PID {pid}) terminado exitosamente")
        except psutil.NoSuchProcess:
            print(f"[INFO] Proceso {process.name} (PID {pid}) ya no existe en el sistema")
        except psutil.AccessDenied:
            print(f"[WARN] Sin permisos para terminar proceso {process.name} (PID {pid})")
        except Exception as e:
            print(f"[ERROR] No se pudo terminar proceso {process.name} (PID {pid}): {e}")
        
        print(f"[OK] Memoria liberada para proceso {process.name} (PID {pid})")
    
    def compact_memory(self):
        """
        Compacta la memoria (solo para particiones variables)
        
        Raises:
            ValueError: Si no se han configurado particiones variables
        """
        if self.partition_type != PartitionType.VARIABLE:
            raise ValueError("La compactación solo está disponible para particiones variables")
        
        free_space = self.variable_manager.compact_memory(self.simulation_memory)
        if free_space is not None:
            print(f"[OK] Memoria compactada: {free_space} MB libres al final")
    
    def calculate_fragmentation(self) -> Dict[str, Any]:
        """
        Calcula la fragmentación según el tipo de particionamiento
        
        Returns:
            Dict con información de fragmentación
        """
        if self.partition_type == PartitionType.FIXED:
            internal_frag = self.fixed_manager.calculate_fragmentation()
            return {
                'type': 'Interna',
                'internal_fragmentation': internal_frag,
                'external_fragmentation': 0,
                'description': f'{internal_frag} MB desperdiciados dentro de particiones'
            }
        
        elif self.partition_type == PartitionType.VARIABLE:
            frag_info = self.variable_manager.calculate_fragmentation()
            return {
                'type': 'Externa',
                'internal_fragmentation': 0,
                'external_fragmentation': frag_info['external_fragmentation'],
                'num_holes': frag_info['num_holes'],
                'largest_hole': frag_info['largest_hole'],
                'total_free': frag_info['total_free'],
                'description': f"{frag_info['num_holes']} huecos, {frag_info['total_free']} MB libres"
            }
        
        return {
            'type': 'Ninguna',
            'internal_fragmentation': 0,
            'external_fragmentation': 0,
            'description': 'No configurado'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del uso de memoria
        
        Returns:
            Dict con estadísticas completas
        """
        partitions = self._get_current_partitions()
        
        used_memory = sum(p.get_used_space() for p in partitions)
        free_memory = self.simulation_memory - used_memory
        
        assigned_processes = sum(1 for p in self.selected_processes if p.is_assigned())
        total_processes = len(self.selected_processes)
        
        free_partitions = sum(1 for p in partitions if p.is_free)
        
        usage_percent = (used_memory / self.simulation_memory * 100) if self.simulation_memory > 0 else 0
        
        # Calcular el mayor espacio libre disponible
        largest_free_space = max((p.size for p in partitions if p.is_free), default=0)
        
        return {
            'total_memory': self.simulation_memory,
            'used_memory': used_memory,
            'free_memory': free_memory,
            'largest_free_space': largest_free_space,
            'usage_percent': round(usage_percent, 2),
            'total_partitions': len(partitions),
            'free_partitions': free_partitions,
            'occupied_partitions': len(partitions) - free_partitions,
            'total_processes': total_processes,
            'assigned_processes': assigned_processes,
            'failed_processes': total_processes - assigned_processes,
            'assignment_rate': round((assigned_processes / total_processes * 100), 2) if total_processes > 0 else 0
        }
    
    def _get_current_partitions(self) -> List[Partition]:
        """Retorna las particiones del manager activo"""
        if self.partition_type == PartitionType.FIXED:
            return self.fixed_manager.get_partitions()
        elif self.partition_type == PartitionType.VARIABLE:
            return self.variable_manager.get_partitions()
        return []
