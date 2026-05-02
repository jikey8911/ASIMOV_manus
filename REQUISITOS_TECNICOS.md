# Requisitos Tecnicos e Instalacion

Este proyecto hoy es un esqueleto base en Python. No depende todavia de librerias externas para arrancar.

## Donde corre

Corre como aplicacion Python local dentro de tu VM.

- Sistema recomendado: Ubuntu 22.04 LTS o 24.04 LTS
- CPU: 2 vCPU minimo, 4 vCPU recomendado
- RAM: 4 GB minimo, 8 GB recomendado
- Disco: 20 GB minimo, 40 GB recomendado
- Red: salida a internet para clonar repositorio, instalar paquetes y consumir APIs

## Requisitos minimos para esta version

Instala esto en la VM:

- `git`
- `python3` 3.11 o superior
- `python3-venv`
- `python3-pip`

## Instalacion en Ubuntu

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

## Preparar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd ASIMOV_manus
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecutar

Como el paquete esta dentro de `src/`, debes exportar `PYTHONPATH`:

```bash
export PYTHONPATH=src
python -m asimov.main
```

Si todo esta bien, veras una salida tipo `OrchestrationResult(...)`.

## Variables de entorno

Para esta base no son obligatorias. Cuando avances a una version real, normalmente vas a necesitar:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GROQ_API_KEY` o proveedor equivalente
- credenciales de bases de datos
- tokens de plataformas externas

## Puertos

Esta version no abre puertos ni expone servicios HTTP.

Si luego agregas frontend o API, los mas probables serian:

- `8000` para API Python
- `3000` o `5173` para frontend

## Requisitos para una version mas completa

Si quieres llevar ASIMOV a una arquitectura operativa real, ademas de lo anterior normalmente conviene instalar o preparar:

### Python y orquestacion

- `langgraph`
- `langchain`
- `pydantic`
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `psycopg` o driver de base de datos equivalente

### Modelos locales

- `Ollama` si vas a correr modelos locales facil de administrar
- o `vLLM` si vas a servir modelos con mas control

### Automatizacion y navegacion

- Playwright o Selenium si vas a operar interfaces web
- Chromium o Google Chrome en la VM

### Infraestructura

- PostgreSQL para persistencia
- Redis para colas, cache o señales
- Docker opcional si quieres empaquetar servicios
- Nginx opcional si luego publicas API o dashboard

## Recomendacion por fases

### Fase 1: solo correr este repo

Necesitas unicamente:

- `git`
- `python3`
- `python3-venv`
- `python3-pip`

### Fase 2: convertirlo en backend real

Agrega:

- FastAPI
- base de datos
- variables de entorno
- servicio systemd o Docker

### Fase 3: multiagente con modelos locales

Agrega:

- Ollama o vLLM
- LangGraph
- Redis
- monitoreo y logs

## Comandos de verificacion utiles

```bash
python --version
pip --version
git --version
```

Verificar arranque:

```bash
export PYTHONPATH=src
python -m asimov.main
```

## Estado actual del proyecto

Hoy este repositorio:

- si corre en una VM limpia con Python
- no requiere GPU
- no requiere Docker
- no requiere base de datos
- no requiere variables de entorno obligatorias

## Siguiente paso recomendado

Si tu objetivo inmediato es clonar y ejecutar, con este documento basta.

Si tu objetivo es dejar la VM lista para la siguiente etapa de desarrollo, el siguiente paquete razonable seria:

```bash
sudo apt install -y git python3 python3-venv python3-pip build-essential
```
