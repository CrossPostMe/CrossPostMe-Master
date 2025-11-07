# 🚀 Deployment Quick Reference

Quick access guide for deploying CrossPostMe to production.

---

## 🔑 Credentials Summary

### Hostinger (Frontend Hosting)

- **SSH Host:** 82.180.138.1
- **SSH Port:** 65002
- **SSH Username:** u132063632
- **SSH Password:** P@ndaGod99$
- **Deployment Path:** public_html/
- **Live URL:** https://www.crosspostme.com

### Render (Backend Hosting)

- **Dashboard:** https://dashboard.render.com/
- **Service ID:** srv-d3r0mnd6ubrc738aj5og
- **User:** dearthdiggler
- **Repository:** CrossPostMe_MR (GitHub)
- **Live URL:** https://crosspostme-backend.onrender.com

### MongoDB Atlas (Database)

- **Dashboard:** https://cloud.mongodb.com/
- **Email:** crosspostme@gmail.com
- **Cluster:** cluster0.fkup1pl.mongodb.net
- **Database Name:** crosspostme2
- **Service Name:** Crosspostmeservice
- **Connection String:** (See .env files)

### Upstash Redis (Cache)

- **Dashboard:** https://console.upstash.com/
- **Endpoint:** crack-blowfish-19241.upstash.io
- **REST URL:** https://crack-blowfish-19241.upstash.io

### Docker Hub

- **Username:** (from DOCKER_PAT)
- **Description:** DOCKER_PAT
- **PAT:** dckr_pat_cwJWLs59Meru_6GqN7aMrpY4uIQ

### Canvas/Claude Integration

- **Canvas URL:** https://claude.ai/lti/launch
- **Canvas Email:** jdominick490@insite.4cd.edu
- **Canvas Password:** sc6LeKbL\*XsMYkq
- **Client ID:** gen-lang-client-0770825656

---

## 📦 Backend Deployment (Render)

### Option 1: Automatic (Git Push)
