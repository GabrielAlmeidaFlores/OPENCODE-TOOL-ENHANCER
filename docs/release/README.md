# Release Process

> **Status:** Stable · **Last verified:** 2026-11-13 · **Evidence:** workflow and version check verified locally

## Version sources

| File | Purpose |
|---|---|
| `VERSION` | Human-readable release version |
| `packages/toolwright_cli/pyproject.toml` | Wheel version; must match `VERSION` |
| Git tag | `v<VERSION>` |

A test fails when `VERSION` and the package version differ. Bump both together.

## Before tagging

1. Complete `docs/RELEASE_CHECKLIST.md`.
2. Run `make ci` and `make lint`.
3. Run `./scripts/release/local_release_check.sh` to reproduce the wheel and checksum build.
4. Confirm the CI run for the release commit is green.
5. Update `CHANGELOG.md` and run `toolwright catalog verify --check-drift`.

## Create a release

```bash
python3 scripts/release/check_version.py
git tag -a "v$(cat VERSION)" -m "Release $(cat VERSION)"
git push origin "v$(cat VERSION)"
```

`./scripts/release/local_release_check.sh` reproduces the wheel build and checksum locally. Pushing the tag triggers `.github/workflows/release.yml`:

1. Verifies the tag matches `VERSION`.
2. Builds the `toolwright-cli` wheel.
3. Writes `SHA256SUMS`.
4. Creates a GitHub release with the wheel and checksum file.

The workflow never stages or commits. It only publishes artifacts for the tag.

## Release history

| Version | Date | Assets | Verification |
|---|---|---|---|
| `v0.1.0` | 2026-11-12 | `ote_cli-0.1.0-py3-none-any.whl`, `SHA256SUMS` | Checksum verified; wheel installed in a clean venv and reports `0.1.0` |
| `v0.1.1` | 2026-11-12 | `ote_cli-0.1.1-py3-none-any.whl`, `SHA256SUMS` | Checksum verified |
| `v0.1.2` | 2026-11-12 | `ote_cli-0.1.2-py3-none-any.whl`, `SHA256SUMS` | Checksum verified |
| `v0.2.0` | 2026-11-13 | `toolwright_cli-0.2.0-py3-none-any.whl`, `SHA256SUMS` | Checksum verified; released from commit `f978b46` |

Releases up to `v0.1.2` used the historical `ote-cli` package and `ote` command. `v0.2.0` is the first ToolWright-named release.

## Verify a release

```bash
gh release download "v$(cat VERSION)" --dir /tmp/toolwright-release
cd /tmp/toolwright-release
shasum -a 256 -c SHA256SUMS
python3 -m venv /tmp/toolwright-verify
/tmp/toolwright-verify/bin/pip install ./*.whl
/tmp/toolwright-verify/bin/toolwright --version
```

## Rollback

- Delete the GitHub release and tag if the artifact is wrong.
- Revert the version bump in a new commit; never rewrite published tags.
- Installed projects roll back with `toolwright rollback` or reinstall a previous profile commit.

## Upstream drift

`.github/workflows/upstream-drift.yml` runs weekly and reports the pinned source commits against their remotes. The scheduled workflow stays green and publishes a table in the job summary; network errors are reported as `unknown` rather than failing the run. Pass `--fail-on-drift` when gating a release.

```bash
python3 scripts/maintenance/check_upstream_drift.py
```

## References

- `docs/RELEASE_CHECKLIST.md`
- `docs/provenance/registry.yml`
- `CHANGELOG.md`
