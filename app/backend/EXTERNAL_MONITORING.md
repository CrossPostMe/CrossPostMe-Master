# External Monitoring Setup

## Sentry (Error Tracking)

- Add `SENTRY_DSN` to your backend environment (local `.env`, Render, Railway, etc.)
- Example `.env` entry:

  SENTRY_DSN=https://<your-key>@o<org-id>.ingest.sentry.io/<project-id>

- Errors and exceptions in FastAPI will be reported to Sentry automatically.
- See <https://docs.sentry.io/platforms/python/guides/fastapi/> for more options.

## UptimeRobot (Uptime Alerts)

- Go to <https://uptimerobot.com/> and create a free account.
- Add a new HTTP(s) monitor for your `/api/ready` endpoint (e.g., `https://yourdomain.com/api/ready`).
- Set alert contacts (email, SMS, Slack, etc.) for downtime notifications.
- You can also monitor `/api/health` for deeper diagnostics.

## Prometheus/Grafana (Optional)

- For custom metrics and dashboards, add a `/metrics` endpoint and run Prometheus/Grafana via Docker Compose.
- See <https://fastapi-utils.davidmontague.xyz/monitoring/prometheus.html> for FastAPI integration.

---

**Summary:**

- Sentry integration is now scaffolded; add your DSN to start tracking errors.
- UptimeRobot can monitor your health endpoints for uptime alerts.
- For advanced metrics, consider Prometheus/Grafana.
