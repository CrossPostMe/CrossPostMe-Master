# Frontend Error Tracking Setup

## Sentry (React)

- Add `REACT_APP_SENTRY_DSN` to your frontend environment (`.env`, `.env.local`, or deployment platform).
- Example `.env` entry:

  ```env
  REACT_APP_SENTRY_DSN=https://<your-key>@o<org-id>.ingest.sentry.io/<project-id>
  ```

- Errors and exceptions in React will be reported to Sentry automatically.
- Uncaught errors in components will show a dialog and be sent to Sentry.
- See <https://docs.sentry.io/platforms/javascript/guides/react/> for more options.

---

**Summary:**

- Sentry integration is now scaffolded for the frontend; add your DSN to start tracking errors.
- You can customize the error boundary fallback UI as needed.
