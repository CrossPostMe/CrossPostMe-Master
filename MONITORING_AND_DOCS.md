# Monitoring & Documentation Setup

## Monitoring

### Sentry (Error Tracking)

- Add your SENTRY_DSN to backend `.env`.
- Errors in FastAPI will be reported automatically.
- Docs: https://docs.sentry.io/platforms/python/guides/fastapi/
- Monitor `/api/ready` and `/api/health` endpoints.

### Prometheus/Grafana (Metrics)

```yaml
  prometheus:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    depends_on:
      - backend

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
```

- Docs: https://fastapi-utils.davidmontague.xyz/monitoring/prometheus.html

## Documentation

- Onboarding: Add setup steps to `README.md`.
- Environment Variables: Document all required secrets in `.env.example` and `README.md`.
- Deployment: Add guides for Hostinger, Render, and Docker Compose.

- [ ] UptimeRobot monitors configured
- [ ] API docs available at `/docs`
- [ ] All secrets and env vars documented
- [ ] Deployment guides up to date
- API Docs: Use FastAPI's built-in `/docs` (Swagger UI).
