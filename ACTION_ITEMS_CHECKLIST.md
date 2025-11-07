# Prioritized Action Items Checklist

This checklist consolidates all findings from the code quality and link analysis report into a prioritized list of actionable items.

---

### P1: High-Priority (Critical User-Facing Bugs)

- [ ] **Fix App Store & Google Play Links:** The download links on the landing pages (`app/landing/src/App.jsx` and its variants) are placeholders (`href="#"`). These are critical dead ends and must be updated with the correct URLs.

### P2: Medium-Priority (Code Health & Build Stability)

- [ ] **Delete Redundant `App.js`:** Delete the old `app/frontend/src/App.js` file to remove duplicate routing logic and prevent future build conflicts.
- [ ] **Delete Redundant Landing Page Files:** Delete the duplicate `.js` files in `app/landing/src` and `app/landing/variant-*` directories to clean up the project.

### P3: Low-Priority (Best Practices & Configuration)

- [ ] **Create Ruff Configuration:** Create a `pyproject.toml` file at the project root to enable a more comprehensive set of linting rules for your Python code.
- [ ] **(Optional) Enable OSV Scanner:** Consider re-enabling `osv-scanner` in `trunk.yaml` for enhanced dependency vulnerability scanning.

### P4: Manual QA Required (Cannot be Automated by Me)

- [ ] **Verify Toaster Actions:** Manually review every usage of the `useToast()` hook to ensure that a meaningful "action" is provided where necessary.
- [ ] **Verify Navbar Functionality:** Manually test all links in the `Navbar.jsx` component (`Dashboard`, `My Ads`, etc.) to confirm they navigate correctly for an authenticated user.
