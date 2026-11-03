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
3. Update relevant documentation and docs/verification.md after each major phase,
   recording what was implemented, the commands/checks run and their outcomes,
   and any remaining limitations, deferrals, or blockers. Preserve earlier phase evidence.
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


## GitHub Delivery & Session Continuity

### Development Checkpoints
- After each completed phase, run pytest, Ruff lint,
  and Ruff format checks.
- Update `docs/verification.md` with test results.
- Commit verified changes using descriptive messages.
- Push completed work to `origin/main`.
- Verify GitHub Actions passes when available.
- Never force-push, commit secrets, or push failing code.

### Persistent Progress Tracking
Maintain `docs/PROGRESS.md` throughout development.

Update it after meaningful milestones with:
- Current phase and status
- Completed and outstanding tasks
- Important technical decisions
- Files changed
- Tests performed and their results
- Known blockers
- Latest verified commit
- Exact next steps

### Session Recovery
If a session ends due to usage limits, context limits,
or interruptions:

1. Preserve completed work and update `docs/PROGRESS.md`
   whenever tools remain available.
2. Commit and push verified checkpoints when possible.
3. Clearly label incomplete or untested work.
4. Never discard uncommitted changes to restore state.

At the beginning of every new session:
1. Read `AGENTS.md` and `docs/PROGRESS.md`.
2. Inspect `git status` and recent commits.
3. Compare repository state with the progress notes.
4. Resume from the last verified checkpoint.

Do not rely on previous chat context for continuity.
Never claim tests, commits, or pushes succeeded
without verifying them.
