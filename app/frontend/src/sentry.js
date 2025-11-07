// Sentry error tracking setup for React frontend
// Place this in src/sentry.js and import in src/index.js

import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [new BrowserTracing()],
  // Adjust sample rate for performance monitoring
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
});

// Optionally, wrap your App in Sentry.ErrorBoundary in src/index.js:
// <Sentry.ErrorBoundary fallback={<p>An error occurred</p>} showDialog>
//   <App />
// </Sentry.ErrorBoundary>
