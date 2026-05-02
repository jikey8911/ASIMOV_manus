# ASIMOV Manus

Base estructural para un sistema multiagente jerárquico inspirado en el documento `ASIMOV.txt`.

Guia de entorno e instalacion: `REQUISITOS_TECNICOS.md`

## Estructura

- `src/asimov/core`: modelos y contratos comunes.
- `src/asimov/levels/level1`: agentes estratégicos.
- `src/asimov/levels/level2`: ciclo científico y UAEs tácticas.
- `src/asimov/levels/level3`: agentes ejecutores.
- `src/asimov/support`: UAEs de apoyo.
- `src/asimov/cycles`: orquestación de ciclos A y B.

## Idea general

El sistema separa la operación en tres niveles:

1. `Nivel 1`: detecta oportunidades y define objetivos.
2. `Nivel 2`: formula hipótesis, diseña experimentos, analiza resultados y documenta estrategias.
3. `Nivel 3`: ejecuta tareas operativas persistentes sobre las estrategias aprobadas.

Además, existen UAEs de apoyo para credenciales, marketing, broker financiero, interfaz de usuario y evolución tecnológica.

## Ejecutar demo

```bash
$env:PYTHONPATH='src'; python -m asimov.main
```
