# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Run Application**: `python app.py` (runs on port 5001)
- **Install Dependencies**: `pip install flask`

## Architecture & Structure

### High-Level Architecture
Spendly is a lightweight Flask application following a classic Server-Side Rendering (SSR) pattern using Jinja2 templates.

### Key Components
- **Backend (`app.py`)**: Handles all routing, request processing, and template rendering. Currently contains both active routes (landing, auth) and placeholder routes for future implementation (profile, expense CRUD).
- **Templates (`templates/`)**:
    - `base.html`: The master layout containing the navigation bar, footer, and global CSS/JS links.
    - Feature-specific templates: Extend `base.html` to provide page-specific content.
- **Static Assets (`static/`)**:
    - `css/style.css`: Global styles, design tokens (CSS variables), and shared components.
    - `css/landing.css`: Specialized styles for the landing page hero and visuals.
    - `js/`: Client-side logic (e.g., landing page modal interactions).

### Design System
The project uses a custom design system defined in `:root` variables in `style.css`, utilizing `DM Serif Display` for headings and `DM Sans` for body text.
