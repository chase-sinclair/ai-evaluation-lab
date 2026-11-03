# Working agreements

- This is an empirical research framework. Protect deterministic grading and experiment isolation.
- Prefer small, typed implementations and high-signal offline tests.
- Put new experiment logic in `experiments/<name>`; keep the runner domain-agnostic.
- Default to offline execution. Paid requests require explicit opt-in, finite positive spending and request limits, bounded output, and owner-approved protocol.
- Check licensing and get owner approval before large downloads or committing third-party benchmark files.
- Never fabricate findings, grades, usage, costs, or source verification. Mock outcomes test software only.
- Never put credentials, private client data, `.env`, downloaded caches, or raw results in Git.
- Run tests and Ruff before reporting completion. Record implementation, verification, deferrals, and blockers.

- 
## Git and GitHub Delivery Workflow

After completing each implementation phase:

1. Run pytest, Ruff lint, and Ruff format checks.
2. Review changes for unintended modifications,
   credentials, caches, and generated artifacts.
3. Update relevant documentation and
   docs/verification.md.
4. Commit verified changes with a descriptive message.
5. Push completed changes to origin/main.
6. Verify GitHub Actions passes, when configured.
7. Report the commit SHA, tests passed, changes made,
   and any remaining issues.

Rules:
- Never push code that fails required checks.
- Never commit credentials, raw results, or caches.
- Never force-push or rewrite Git history.
- Do not commit unrelated changes.
- If a phase is blocked, report it rather than
  marking it complete.
- Leave the working tree clean after successful delivery.

