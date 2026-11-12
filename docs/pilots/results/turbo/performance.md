# Pilot Performance Notes

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

Scope: read-only static inspection of 5 files in the hashing / file-walk path.
No tests were run and no other files were modified.

## Likely hotspots

- **Per-file hashing is strictly sequential, and each file re-resolves its `.gitattributes` entry.**
  Evidence: `crates/turborepo-scm/src/manual.rs:40-57` iterates the input list in a plain `for` loop, calling `hash_file_with_attrs` one file at a time; `manual.rs:73-77` does an attrs lookup per file before dispatching to `manual_hash_file_maybe_normalized` (`crates/turborepo-scm/src/crlf.rs:626`). The identical shape appears again in `hash_discovered_files` (`manual.rs:113-120`). With hundreds of thousands of package files this leaves every core but one idle, and the work is I/O + hashing, which parallelizes almost linearly.

- **External lockfile inputs are read fully into memory and hashed serially.**
  Evidence: `crates/turborepo-repository/src/package_graph/javascript.rs:307-318` loops over `used_paths` and does `std::fs::read(&physical_path)` followed by `xxh64(...)` per path, one file at a time (`javascript.rs:315-317`). This is unbounded per-file allocation (a single large lockfile or vendored artifact is fully resident), no parallelism, and it also canonicalizes each path with `dunce::canonicalize` inside the loop (`javascript.rs:310`), i.e. an extra syscall per input on top of the read. Vendor-heavy repos pay this on every run that needs resolution.

- **Fallback (non-index) SCM path mixes an `O(n)` symlink stat pass with the hash, and the fs walk falls back to a mutex-guarded map.**
  Evidence: `crates/turborepo-scm/src/package_deps.rs:400-406` filters every hashed key through `crate::hash_object::has_symlink(...)`, adding one `lstat` per file before hashing. Separately, the copy planner's parallel walk funnels results through `Mutex<HashMap>` (`crates/turborepo-fs/src/lib.rs:224-230`) and re-sorts each source's entries by depth (`fs/lib.rs:241-249`), while the non-parallel branch is a plain sequential `for entry in builder.build()` (`fs/lib.rs:216-220`). Contention plus sort-all-then-copy means the "parallel" path can degrade toward serial on wide trees.

## Measurement plan

Build a synthetic monorepo (e.g. 2,000 packages x 100 small files, plus one 200 MB file and a 5,000-entry `.gitattributes`) and measure the cold and warm task-hash path with `hyperfine`, keeping a baseline commit for comparison:

```sh
git worktree add /tmp/perf-baseline HEAD
# in each tree, build a release binary
cargo build --release -p turbo

# cold: drop the local cache/daemon state between runs
hyperfine --warmup 1 --runs 10 --prepare 'rm -rf .turbo/cache' \
  './target/release/turbo run build --dry=json > /dev/null'

# attribute the time: syscall counts and flamegraph on a single warm run
sudo dtrace -c './target/release/turbo run build --dry=json > /dev/null' -n 'syscall:::entry { @[probefunc] = count(); }'
perf record -g -- ./target/release/turbo run build --dry=json > /dev/null && perf report --stdio
```

Pass/fail signal: report wall-clock p50/p95, total `open`/`lstat`/`read` syscall counts, and the share of samples in `manual::hash_files` / `hash_file_inputs`. Treat the change as a win only if p50 drops with syscall counts unchanged or lower — a drop that comes from skipping work (fewer files hashed) is a correctness bug, not a speedup.
