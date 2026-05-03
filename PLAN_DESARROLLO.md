# Plan de Desarrollo ASIMOV

Fecha: 2026-05-03
Repositorio: `/home/ubuntu/ASIMOV_manus`

## Objetivo

Evolucionar ASIMOV desde un esqueleto funcional a una arquitectura operativa por niveles:

- Nivel 1: estrategia y seleccion de oportunidades.
- Nivel 2: ciclo tactico con LangGraph, CrewAI, Skyvern, OpenClaw y Ollama.
- Nivel 3: ejecucion, integraciones, recoleccion de datos y control de calidad.
- API: exponer estado, salud y ejecucion del sistema.

## Estado Actual de Implementacion

### Estado general

- El backend FastAPI esta operativo en `:8000`.
- Redis, PostgreSQL y Ollama estan corriendo en la VM.
- OpenClaw limpio esta instalado y operativo en `:18789`.
- El canal de Telegram de OpenClaw esta activo.
- Ollama tiene disponible el modelo local `qwen2.5:3b`.

### Estado por nivel

#### Nivel 1
- Implementado como capa estrategica base.
- Detecta oportunidades mediante RSS real y las procesa con agentes.
- Estado: 🔶 Funcional, pero agentes de planeación y riesgo aún son heurísticos.

#### Nivel 2
- Se implementaron agentes reales utilizando **ChatGoogleGenerativeAI (Gemini)**.
- El grafo táctico de LangGraph ahora utiliza salida estructurada para Hipótesis, Experimentos y Estrategias.
- Conexión verificada con el contexto táctico real de OpenClaw y Ollama.
- Estado: ✅ Operativo con LLM real.

#### Nivel 3

- Sigue siendo base funcional.
- Ejecuta tareas de integracion, datos y control de calidad.
- Estado: funcional, pero aun simplificado.

## Tareas Completadas

### Infraestructura y entorno

- Instalacion de VM y entorno Python.
- Instalacion de dependencias backend.
- Dockerizacion de ASIMOV.
- Integracion de Redis, PostgreSQL y Ollama.
- Instalacion limpia de OpenClaw en ruta separada.
- Configuracion de credenciales en `.env`.
- Verificacion de modelos OpenAI visibles desde OpenClaw.
- Verificacion de Ollama desde la VM.

### Backend

- API FastAPI base creada.
- Endpoints `/`, `/health`, `/api/v1/system/status` y `/api/v1/system/run` disponibles.
- Health checks de Redis, PostgreSQL y Ollama implementados.

### Nivel 2

- `IdentityUAE` actualizado para trabajar con OpenClaw real.
- Consolidacion de UAE de credenciales con inventario de servicios, API keys, sesiones y backends declarados.
- `TacticalContext` agregado al dominio compartido.
- `scientific_cycle.py` ampliado para:
  - construir hipotesis con contexto tactico,
  - diseñar experimentos con herramientas reales,
  - evaluar conectividad OpenClaw/Ollama,
  - sintetizar una estrategia tactica utilizable.
- `orchestrator.py` ampliado para retornar datos tacticos utiles.
- `runtime.py` ampliado para exponer estado tactico mas rico.

## Pendiente por Implementar

### Nivel 2 completado reciente
- Implementación de agentes reales con Gemini en `scientific_cycle.py`.
- Uso de `with_structured_output` para garantizar consistencia de datos.
- Integración de trazas y contexto táctico enriquecido.

### Nivel 2 pendiente funcional

- LangGraph runtime configurado para leer `LANGGRAPH_API_KEY` y exponer estado de tracing sin ejecutar procesos.

- Reemplazar heuristicas por flujo real con LangGraph.
- Integrar CrewAI como coordinador de subagentes tacticos.
- Conectar Skyvern para automatizacion UI real donde no haya API.
- Conectar skills/acciones reales de OpenClaw en vez de solo contexto y wrappers.
- Agregar persistencia de experimentos tacticos en PostgreSQL.
- Registrar eventos tacticos y trazas en Redis/PostgreSQL.

### Nivel 3 pendiente

- Convertir tareas ejecutoras en acciones reales sobre APIs/servicios.
- Agregar pipeline de ejecucion asincrona y control de reintentos.
- Implementar auditoria de ejecucion y telemetria.

### API pendiente

- Exponer endpoints especificos para nivel 2.
- Endpoint especifico para estado de credenciales UAE.
- Exponer estado de herramientas y conectividad por nivel.
- Exponer historial de corridas y resultados tacticos.

## Siguiente Paso Recomendado

1. Reiniciar el backend correcto de ASIMOV en la VM.
2. Validar que la API exponga el nuevo estado del nivel 2.
3. Si la validacion es correcta, pasar a implementar el flujo real de LangGraph en nivel 2.

## Riesgos Tecnicos Actuales

- Hay mas de una forma de levantar ASIMOV en la VM y eso puede dejar procesos sirviendo codigo viejo.
- OpenClaw ya esta autenticado por entorno, pero parte de su configuracion fina sigue dependiendo de reinicios limpios del gateway.
- El nivel 2 ya tiene mejor modelo de dominio, pero aun no ejecuta automatizacion multiagente real.
