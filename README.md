# Documento de Requerimientos - Monitor de Sistema

## 1. Información General del Proyecto

### 1.1 Nombre del Proyecto
**Monitor de Sistema (Activity Monitor)**

### 1.2 Descripción General
Aplicación de escritorio desarrollada en Python para monitorear en tiempo real el rendimiento del sistema operativo, gestionar procesos, administrar archivos USB y controlar la memoria del sistema.

### 1.3 Objetivos
- Proporcionar una interfaz gráfica moderna e intuitiva para visualizar el estado del hardware
- Monitorear en tiempo real el uso de CPU, RAM y almacenamiento
- Simular y gestionar procesos del sistema operativo
- Administrar dispositivos USB y archivos
- Gestionar la memoria del sistema de manera eficiente

### 1.4 Alcance
Aplicación de escritorio multiplataforma con capacidades de monitoreo de sistema para Windows, con posibilidad de extensión a Linux y macOS.

---

## 2. Requerimientos Funcionales

### 2.1 Monitor de Hardware (RF-001)

#### RF-001.1 - Monitoreo de CPU
**Prioridad:** Alta
- **Descripción:** Mostrar información en tiempo real del uso del procesador
- **Criterios de aceptación:**
  - Mostrar porcentaje de uso actual del CPU
  - Mostrar nombre del procesador y número de núcleos
  - Actualizar datos en tiempo real
  - Mostrar gráfico histórico de uso
- **Dependencias:** Librería psutil

#### RF-001.2 - Monitoreo de Memoria RAM
**Prioridad:** Alta
- **Descripción:** Mostrar información en tiempo real del uso de memoria RAM
- **Criterios de aceptación:**
  - Mostrar porcentaje de uso de RAM
  - Mostrar cantidad de memoria usada y total (GB)
  - Mostrar barra de progreso visual
  - Actualizar datos en tiempo real
- **Dependencias:** Librería psutil

#### RF-001.3 - Monitoreo de Almacenamiento
**Prioridad:** Alta
- **Descripción:** Mostrar información del uso del disco duro principal
- **Criterios de aceptación:**
  - Mostrar capacidad total y espacio usado
  - Mostrar espacio libre disponible
  - Mostrar barra de progreso del uso
  - Identificar la unidad principal (C: en Windows)
  - Detallar velocidades de lectura y escritura
- **Dependencias:** Librería psutil

### 2.2 Simulación de Procesos (RF-002)

#### RF-002.1 - Gestión de Procesos
**Prioridad:** Media
**Estado:** Por implementar
- **Descripción:** Simular y gestionar procesos del sistema operativo
- **Criterios de aceptación:**
  - Listar procesos activos del sistema
  - Mostrar ID de proceso (PID)
  - Mostrar uso de CPU y memoria por proceso
  - Permitir finalizar procesos seleccionados
  - Ordenar procesos por diferentes criterios (CPU, memoria, nombre)
  - Buscar procesos específicos
- **Dependencias:** Librería psutil

#### RF-002.2 - Algoritmos de Planificación
**Prioridad:** Media
**Estado:** Por implementar
- **Descripción:** Simular algoritmos de planificación de procesos
- **Criterios de aceptación:**
  - Implementar algoritmo FIFO (First In First Out)
  - Implementar algoritmo Round Robin
  - Implementar algoritmo de Prioridades
  - Visualizar cola de procesos
  - Mostrar tiempo de ejecución y espera
- **Dependencias:** Ninguna (lógica propia)

### 2.3 Archivos USB (RF-003)

#### RF-003.1 - Detección de Dispositivos USB
**Prioridad:** Media
**Estado:** Por implementar
- **Descripción:** Detectar y listar dispositivos USB conectados
- **Criterios de aceptación:**
  - Detectar automáticamente cuando se conecta un USB
  - Mostrar información del dispositivo (nombre, capacidad, sistema de archivos)
  - Notificar al usuario sobre nuevas conexiones
  - Detectar cuando se desconecta un USB
- **Dependencias:** Librería psutil, watchdog o pyusb

#### RF-003.2 - Exploración de Archivos USB
**Prioridad:** Media
**Estado:** Por implementar
- **Descripción:** Navegar y gestionar archivos en dispositivos USB
- **Criterios de aceptación:**
  - Explorar estructura de carpetas del USB
  - Mostrar archivos con sus propiedades (tamaño, fecha, tipo)
  - Copiar archivos desde/hacia el USB
  - Eliminar archivos del USB
  - Buscar archivos en el USB
- **Dependencias:** Librerías estándar de Python (os, shutil)

### 2.4 Administración de Memoria (RF-004)

#### RF-004.1 - Gestión de Memoria Virtual
**Prioridad:** Media
**Estado:** Por implementar
- **Descripción:** Administrar y simular memoria virtual del sistema
- **Criterios de aceptación:**
  - Mostrar uso de memoria swap/paginación
  - Simular algoritmos de reemplazo de páginas
  - Visualizar tabla de páginas
  - Mostrar estadísticas de page faults
- **Dependencias:** Librería psutil

#### RF-004.2 - Optimización de Memoria
**Prioridad:** Baja
**Estado:** Por implementar
- **Descripción:** Herramientas para optimizar el uso de memoria
- **Criterios de aceptación:**
  - Liberar memoria cache
  - Identificar procesos que consumen más memoria
  - Sugerir optimizaciones
- **Dependencias:** Librería psutil

---

## 3. Requerimientos No Funcionales

### 3.1 Interfaz de Usuario (RNF-001)
**Prioridad:** Alta
- Interfaz gráfica moderna con tema oscuro
- Diseño responsive y adaptable
- Navegación mediante pestañas
- Colores de acento azul (#3399FF)
- Tipografía clara y legible (Arial)
- Bordes redondeados y sombreados sutiles

### 3.2 Rendimiento (RNF-002)
**Prioridad:** Alta
- Actualización de datos en tiempo real (cada 1-2 segundos)
- Consumo mínimo de recursos del sistema
- Tiempo de respuesta de la interfaz < 100ms
- Inicio de aplicación < 3 segundos

### 3.3 Usabilidad (RNF-003)
**Prioridad:** Alta
- Interfaz intuitiva sin necesidad de manual
- Información claramente organizada
- Mensajes de error descriptivos
- Tooltips informativos

### 3.4 Portabilidad (RNF-004)
**Prioridad:** Media
- Compatible con Windows 10/11
- Código preparado para extensión a Linux y macOS
- Uso de librerías multiplataforma

### 3.5 Mantenibilidad (RNF-005)
**Prioridad:** Media
- Código modular y bien estructurado
- Documentación en código (docstrings)
- Separación clara entre GUI y lógica de negocio
- Uso de componentes reutilizables

### 3.6 Seguridad (RNF-006)
**Prioridad:** Media
- Permisos adecuados para operaciones del sistema
- Confirmación antes de acciones críticas (finalizar procesos)
- Validación de entradas del usuario

---

## 4. Restricciones Técnicas

### 4.1 Tecnologías Obligatorias
- **Lenguaje:** Python 3.10 o superior
- **Framework GUI:** CustomTkinter
- **Librería de Sistema:** psutil
- **Control de Versiones:** Git

### 4.2 Arquitectura
```
activity_monitor/
├── main.py                 # Punto de entrada de la aplicación
├── src/
│   ├── backend/           # Lógica de negocio y acceso al sistema
│   └── gui/               # Interfaz gráfica
│       ├── gui_monitor.py  # Ventana principal
│       ├── components/     # Componentes reutilizables
│       │   ├── cpu_card.py
│       │   ├── ram_card.py
│       │   └── storage_card.py
│       └── tabs/           # Pestañas de la aplicación
│           └── tab_hardware.py
```

---

## 5. Dependencias del Proyecto

### 5.1 Dependencias Actuales
- `customtkinter` - Framework para interfaz gráfica moderna
- `psutil` - Acceso a información del sistema

### 5.2 Dependencias Futuras (Planificadas)
- `matplotlib` - Para gráficos de rendimiento histórico
- `watchdog` - Para monitoreo de archivos USB
- `pillow` - Para manipulación de imágenes e íconos

---

## 6. Casos de Uso

### CU-001: Ver Estado del Hardware
**Actor:** Usuario
**Precondiciones:** Aplicación iniciada
**Flujo Principal:**
1. Usuario inicia la aplicación
2. Sistema muestra pestaña "Monitor de Hardware" por defecto
3. Sistema actualiza información de CPU, RAM y almacenamiento cada 2 segundos
4. Usuario visualiza métricas en tiempo real

**Postcondiciones:** Usuario conoce el estado actual del sistema

### CU-002: Gestionar Procesos (Por implementar)
**Actor:** Usuario
**Precondiciones:** Aplicación iniciada
**Flujo Principal:**
1. Usuario selecciona pestaña "Simulación Procesos"
2. Sistema muestra lista de procesos activos
3. Usuario selecciona un proceso
4. Usuario solicita finalizar proceso
5. Sistema solicita confirmación
6. Usuario confirma
7. Sistema finaliza el proceso

**Postcondiciones:** Proceso finalizado correctamente

### CU-003: Explorar USB (Por implementar)
**Actor:** Usuario
**Precondiciones:** Dispositivo USB conectado
**Flujo Principal:**
1. Usuario conecta dispositivo USB
2. Sistema detecta y notifica nueva conexión
3. Usuario selecciona pestaña "Archivos USB"
4. Sistema muestra contenido del USB
5. Usuario navega por carpetas y archivos

**Postcondiciones:** Usuario accede a archivos USB

---

## 7. Cronograma de Desarrollo

### Fase 1: Completado ✓
- ✓ Estructura básica del proyecto
- ✓ Interfaz principal con pestañas
- ✓ Componentes de tarjetas (CPU, RAM, Almacenamiento)
- ✓ Diseño visual y tema oscuro

### Fase 2: En Desarrollo
- Integración con psutil para datos reales
- Actualización en tiempo real de métricas
- Gráficos de histórico de uso

### Fase 3: Planificada
- Implementación de "Simulación Procesos"
- Algoritmos de planificación
- Gestión de procesos del sistema

### Fase 4: Planificada
- Implementación de "Archivos USB"
- Detección de dispositivos
- Explorador de archivos

### Fase 5: Planificada
- Implementación de "Admin Memoria"
- Gestión de memoria virtual
- Herramientas de optimización

---

## 8. Riesgos y Mitigación

### Riesgo 1: Permisos de Sistema
**Probabilidad:** Media | **Impacto:** Alto
- **Descripción:** Algunas operaciones pueden requerir permisos de administrador
- **Mitigación:** Implementar manejo de excepciones y solicitar elevación de permisos cuando sea necesario

### Riesgo 2: Compatibilidad Multiplataforma
**Probabilidad:** Media | **Impacto:** Medio
- **Descripción:** Diferencias entre sistemas operativos
- **Mitigación:** Usar librerías multiplataforma (psutil) y abstracciones para código específico de SO

### Riesgo 3: Rendimiento
**Probabilidad:** Baja | **Impacto:** Medio
- **Descripción:** La aplicación podría consumir demasiados recursos
- **Mitigación:** Optimizar frecuencia de actualización y usar hilos para operaciones pesadas

---

## 9. Criterios de Aceptación del Proyecto

1. ✓ Interfaz gráfica funcional con 4 pestañas
2. ⏳ Monitoreo en tiempo real de CPU, RAM y almacenamiento
3. ⏳ Gestión completa de procesos del sistema
4. ⏳ Detección y exploración de dispositivos USB
5. ⏳ Administración de memoria virtual
6. ⏳ Documentación técnica completa
7. ⏳ Pruebas funcionales exitosas en Windows

**Leyenda:** ✓ Completado | ⏳ Pendiente

---

## 10. Referencias y Documentación

- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [Python Official Documentation](https://docs.python.org/3/)

---

**Versión del Documento:** 1.0  
**Fecha de Creación:** 25 de enero de 2026  
**Última Actualización:** 25 de enero de 2026  
**Autor:** Equipo de Desarrollo Activity Monitor
