# Architecture

## Initial architecture

Browser -> Next.js frontend -> FastAPI REST API -> PostgreSQL
                                      |
                                      +-> DVSA MOT History API (later)
                                      +-> LLM provider (later)

## Principles

- Keep external API integrations behind service classes.
- Keep route handlers thin; business logic belongs in services.
- Store our own user-entered data in PostgreSQL.
- Treat DVSA data as external source data and normalise it before exposing it to the UI.
- Do not let AI-generated output directly make safety-critical decisions.
- Add complexity only when a feature needs it.
