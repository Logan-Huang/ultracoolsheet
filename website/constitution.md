# Astro-Web Constitution

<!--
Sync Impact Report (v1.1.0):
Version change: 1.0.0 → 1.1.0 (Added CSS styling principle)
Modified principles: Renumbered existing principles IV-VI to V-VII
Added sections: New principle VII (CSS Styling)
Removed sections: None
Templates requiring updates: 
  ✅ plan-template.md (Updated constitution check to include all principles)
  ✅ spec-template.md (Constitution principles applicable)
  ✅ tasks-template.md (Constitution principles applicable)
Follow-up TODOs: None
-->

## Core Principles

### I. FastAPI-First Architecture
Every web endpoint MUST be defined via FastAPI. Jinja2 templates MUST be used for all web page rendering. The API layer MUST be clearly separated from the presentation layer to enable future programmatic access and prototype reuse across other astronomical databases.

### II. Astrodbkit Database Abstraction
Data access MUST use Astrodbkit for SQLite queries. Direct SQL access MUST be avoided. This ensures compatibility with astronomical data standards and facilitates portability to other database backends in future prototypes.

### III. Bokeh for Visualizations
All data visualizations MUST be generated using Bokeh. Visualizations MUST be embedded as interactive components in Jinja2 templates. Exported visualizations MUST support PNG and HTML formats for documentation and presentations.

### IV. CSS for Styling
Website styling MUST use CSS. CSS files MUST be kept separate from HTML templates. Inline styles and JavaScript-based styling frameworks are prohibited to maintain simplicity and facilitate maintenance by astronomers with intermediate-level skills. Use vanilla CSS or minimal CSS frameworks that do not require compilation.

### V. Simplicity Over Elegance (NON-NEGOTIABLE)
Code MUST prioritize clarity and straightforward logic over clever optimizations. Functions MUST be kept small (<50 lines when possible). Complex abstractions and design patterns MUST be avoided unless absolutely necessary. This principle ensures astronomers with intermediate Python skills can maintain and extend the prototype.

### VI. Prototype-Driven Development
Design decisions MUST consider this codebase as a prototype for other astronomical databases. Data models, API endpoints, and UI components MUST be designed with reusability in mind. Clear documentation of data schemas and API contracts is mandatory.

### VII. SQLite-First Storage
The primary database will initially be SQLite for ease of deployment and distribution. Database files MUST be readable by standard SQLite tools for data inspection and backup.

## Technology Stack Requirements

**Backend Framework**: FastAPI ≥0.120.0  
**Template Engine**: Jinja2 (via FastAPI templates)  
**Styling**: CSS (vanilla CSS or minimal frameworks)  
**Database**: SQLite with Astrodbkit ≥2.4  
**Visualization**: Bokeh  
**Language**: Python ≥3.13  
**Deployment**: Development server (uvicorn) for prototype phase  
**Testing**: pytest for integration tests, manual testing for UI flows

## Development Approach

### Code Organization
- `/astro_web/main.py`: FastAPI application entry point
- `/astro_web/routes/`: API route definitions
- `/astro_web/templates/`: Jinja2 HTML templates
- `/astro_web/static/`: CSS files and static assets
- `/astro_web/database/`: Astrodbkit database connection and queries
- `/astro_web/visualizations/`: Bokeh plot generation functions
- `/tests/`: Integration tests for API endpoints

### Documentation Standards
- All functions MUST have docstrings explaining purpose, parameters, and return values
- Data models MUST have clear comments explaining astronomical meaning
- README MUST include setup instructions and database schema overview
- API endpoints MUST be documented with clear request/response examples

### Testing Requirements
- Integration tests MUST verify Astrodbkit queries return expected data structures
- API endpoint tests MUST verify JSON responses for API routes
- Template rendering tests MUST verify pages load without errors
- Visualizations MUST be manually verified to display correctly

## Governance

This constitution supersedes all other development practices. Amendments require:
1. Documentation of rationale
2. Impact assessment on prototype reusability
3. Update to version number following semantic versioning
4. Synchronization with template files

All code reviews MUST verify compliance with these principles. Complexity beyond intermediate Python must be justified with clear comments explaining necessity. The `/speckit.plan` and `/speckit.spec` commands provide runtime development guidance for implementing features while maintaining constitution compliance.

**Version**: 1.1.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
