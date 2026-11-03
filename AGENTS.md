# Working agreements

- This is an empirical research framework. Protect deterministic grading and experiment isolation.
- Prefer small, typed implementations and high-signal offline tests.
- Put new experiment logic in `experiments/<name>`; keep the runner domain-agnostic.
- Default to offline execution. Paid requests require explicit opt-in, finite positive spending and request limits, bounded output, and owner-approved protocol.
- Check licensing and get owner approval before large downloads or committing third-party benchmark files.
- Never fabricate findings, grades, usage, costs, or source verification. Mock outcomes test software only.
- Never put credentials, private client data, `.env`, downloaded caches, or raw results in Git.
- Run tests and Ruff before reporting completion. Record implementation, verification, deferrals, and blockers.
