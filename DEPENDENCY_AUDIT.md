# Dependency Security Audit

**Audit date:** 2026-11-01

**Issue:** [#187 — Conduct Dependency Audit](https://github.com/username-anthony-is-not-available/explorer-mintchain-to-csv/issues/187)

**Tool:** `pip-audit` 2.10.1

## Result

`requirements.txt` and `requirements-dev.txt` were audited together, including resolved transitive dependencies. The scan resolved 33 packages and reported **no known vulnerabilities**.

Command used:

```sh
pip-audit -r requirements.txt -r requirements-dev.txt --progress-spinner off --format=json
```

`pip-audit` uses the PyPA Advisory Database through the PyPI JSON API by default ([tool documentation](https://pypi.org/project/pip-audit/)).

## Resolved package inventory

These are the versions resolved for this audit; they are not a lock file.

| Package | Version | Package | Version |
| --- | --- | --- | --- |
| annotated-types | 0.8.0 | certifi | 2026.10.23 |
| cffi | 2.1.1 | charset-normalizer | 3.5.2 |
| cryptography | 50.0.0 | flake8 | 7.1.0 |
| greenlet | 3.5.6 | idna | 3.20 |
| iniconfig | 2.3.1 | mccabe | 0.7.0 |
| playwright | 1.64.1 | pluggy | 1.7.0 |
| pycodestyle | 2.12.1 | pycparser | 3.12 |
| pydantic | 2.5.2 | pydantic-core | 2.14.5 |
| pyee | 14.0.0 | pyflakes | 3.2.0 |
| pygments | 2.21.0 | pytest | 9.0.3 |
| pytest-base-url | 2.1.0 | pytest-playwright | 0.7.2 |
| pytest-responses | 0.4.0 | python-dotenv | 1.2.2 |
| python-slugify | 8.0.4 | pyyaml | 6.0.3 |
| requests | 2.33.0 | responses | 0.25.8 |
| tenacity | 9.1.2 | text-unidecode | 1.3 |
| tqdm | 4.70.1 | typing-extensions | 4.16.0 |
| urllib3 | 2.8.0 |  |  |

## Notes

This is a point-in-time check for publicly reported vulnerabilities, not a guarantee against unknown or undisclosed issues. The repository has no lock file, so version ranges may resolve differently on a future run. The audit found no vulnerability-based reason to change dependency pins; it does not by itself establish that every pinned package is the newest available release. Re-run the command after dependency changes and periodically to refresh the result.
