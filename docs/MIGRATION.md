# Migration from the unpublished TB3 prototype

The public `eval-evidence` v0.1 line supersedes an unpublished internal prototype named
`tb3-eval-integrity` / `eval-integrity`. No package was released under those identities.
The PyPI name `eval-integrity` is owned by an unrelated project, so this project uses:

- distribution and CLI: `eval-evidence`;
- Python import: `eval_evidence`;
- bundle wire ID: `eval-evidence.bundle/v0.1`.

Prototype bundles using `tb3.eval-integrity.*` are not silently accepted because their
source and required fields differ. Rebuild them from the original run directory using
the Harbor adapter:

```bash
eval-evidence bundle /path/to/harbor-trial -o rebuilt.json
```

Research-specific hint and harness-preregistration validators are intentionally absent
from the general distribution. TB3 Parquet enrichment remains outside the product;
item-validity claims can be supplied through the generic manifest with explicit
provenance.
