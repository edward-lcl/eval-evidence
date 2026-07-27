# Security policy

## Reporting a vulnerability

Report vulnerabilities privately to maintainer **Edward Lue Chee Lip** at
**eluecheelip@gmail.com**. Do not include credentials, private trajectories, provider
prompts, or other sensitive evaluation data in an initial report.

Include the affected Eval Evidence version, command or schema, synthetic reproduction
steps where possible, and impact. Reports concerning path handling, bundle verification,
adapter ambiguity, schema compatibility, or the GitHub Action are in scope.

## Supported versions

Security fixes target the current `0.1.x` line until a newer release line is announced.

## Security boundary

A bundle digest establishes byte identity only. It is not a trusted-runner signature,
proof of physical truth, or evidence that all provider state was disclosed. Eval
Evidence is intended for stable local run directories; it does not isolate an actively
hostile concurrent filesystem. See `docs/TRUST_MODEL.md`.
