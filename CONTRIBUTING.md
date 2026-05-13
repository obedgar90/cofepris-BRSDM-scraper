# Guía de contribución

Gracias por tu interés en contribuir a `cofepris-BRSDM-scraper`.
Este proyecto busca facilitar el acceso ciudadano a información pública de COFEPRIS de forma confiable y reproducible.

## Formas de contribuir

- Reportar errores mediante Issues.
- Proponer mejoras o nuevas funcionalidades.
- Mejorar documentación y ejemplos.
- Enviar Pull Requests con correcciones o refactors.

## Antes de abrir un Issue

- Verifica si ya existe un Issue similar.
- Incluye contexto suficiente para reproducir el problema.
- Usa un título claro y descriptivo.

## Flujo recomendado para Pull Requests

1. Haz un fork del repositorio.
2. Crea una rama descriptiva:
   - `feat/nombre-corto`
   - `fix/nombre-corto`
   - `docs/nombre-corto`
3. Asegúrate de mantener cambios pequeños y enfocados.
4. Escribe o actualiza pruebas antes del cambio funcional (TDD).
5. Ejecuta validaciones locales antes de abrir tu PR.
6. Abre el Pull Request usando la plantilla.

## Estándares de calidad

- Mantén compatibilidad hacia atrás salvo que se acuerde lo contrario.
- Aplica principios SOLID en diseño y responsabilidades.
- Prefiere manejo explícito de errores y mensajes accionables.
- No incluyas secretos, credenciales ni datos sensibles.
- Documenta cualquier cambio operativo.

## Convenciones de cambios

- Commits atómicos y con intención clara.
- Un PR debe resolver un problema específico.
- Si el cambio es grande, divide en PRs más pequeños.

## Qué debe incluir un PR

- Problema que resuelve y por qué.
- Estrategia de solución.
- Evidencia de pruebas ejecutadas.
- Riesgos, supuestos y alcance fuera de PR (si aplica).

## Alcance fuera de contribuciones estándar

Antes de proponer estos cambios, abre un Issue para alinear criterios:

- Cambios de esquema de base de datos.
- Cambios de infraestructura/CI.
- Cambios destructivos sobre datos.
- Dependencias nuevas.

## Código de conducta

Al participar en este repositorio aceptas nuestro [Código de Conducta](CODE_OF_CONDUCT.md).
