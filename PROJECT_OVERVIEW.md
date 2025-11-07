# Project Overview & Current State

This document provides a high-level overview of the CrossPostMe project architecture, technology stack, and the current status of each component. It is intended to be a living document for any developer to quickly understand the state of the environment.

---

## 1. High-Level Architecture

The CrossPostMe project follows a modern, multi-client, "headless" architecture. It is composed of several independent applications that communicate with a central backend via a REST API.

- **`app/backend`**: A FastAPI (Python) application that serves as the core backend. It handles all business logic, database interactions, and user authentication.
- **`app/frontend`**: The main web application, built with React and Vite. This is the primary interface for users to manage their ads.
- **`app/landing`**: A separate marketing website, also built with React and Vite, designed for multi-page A/B testing.
- **`Android` / `IOS`**: Native mobile applications (currently in scaffolding/early development).
- **`supabase`**: An experimental, in-progress Supabase backend being built as a potential replacement for the FastAPI backend. **(Currently NOT integrated).**

---

## 2. Technology Stacks & Status

### a. Backend (`app/backend`)

- **Stack:** Python, FastAPI, MongoDB (via `motor`), `uvicorn`.
- **Status:** **STABLE**. The backend is feature-complete and serves as the production API for all clients.
- **Key Commands (from root):**
  - To start the backend and its database: `docker-compose up backend mongo`

### b. Main Web App (`app/frontend`)

- **Stack:** React, Vite, Tailwind CSS, Playwright (for E2E tests).
- **Status:** **STABLE**. The migration from Create React App to Vite is complete. The application is buildable and all critical user journeys are covered by E2E tests.
- **Key Commands (from `app/frontend`):**
  - To install dependencies: `yarn install`
  - To start the dev server: `yarn start`
  - To run end-to-end tests: `yarn test:e2e`

### c. Landing Pages (`app/landing`)

- **Stack:** React, Vite, Tailwind CSS.
- **Status:** **STABLE**. This project is configured for a multi-page Vite build, allowing for independent A/B testing of different landing page variants.
- **Key Commands (from `app/landing`):**
  - To install dependencies: `npm install`
  - To start the dev server: `npm run dev`

### d. Supabase Backend (`supabase`)

- **Stack:** Supabase, PostgreSQL, Deno/TypeScript (for Edge Functions).
- **Status:** **IN PROGRESS**. The initial database schema has been created in a migration file. This is a new, experimental backend and is **not yet connected** to any frontend application. It is being developed in a separate, parallel effort.

---

## 3. Completed Processes & Key Decisions (as of latest session)

This section documents the most recent, significant changes to the environment.

- **Vite Migration Completed:** Both `app/frontend` and `app/landing` have been successfully migrated from Create React App to Vite, resolving a long series of complex build issues. The final, stable Docker build process is now in place.
- **Code Cleanup & Quality Pass:** A comprehensive code quality review was completed.
  - **Redundant Files Deleted:** Duplicate `.js` files and old route configurations were removed from the frontend projects.
  - **Linter Configuration Enhanced:** A `pyproject.toml` was added to strengthen Ruff's Python linting, and `osv-scanner` was enabled in Trunk.io for security vulnerability scanning.
- **E2E Test Suite Established:** A suite of "AI agent" tests was created using Playwright to automatically verify core user journeys, including authentication (`auth.spec.js`) and navbar navigation (`navbar.spec.js`).
- **Supabase Backend Scaffolding:** The initial foundation for a new, experimental Supabase backend has been laid in the `supabase/` directory. This is a separate effort and does not impact the current, stable application.
