# PILOT_BUG

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

## Suspected bug

`BoundariesConfig` hand-implements `WithMetadata`, but both `add_text` and `add_path` propagate source metadata only into `tags` and `implicit_dependencies`; they never recurse into the package-level `dependencies` and `dependents` fields (`crates/turborepo-boundaries/src/config.rs:92-124`). Those fields are declared as `Spanned<Permissions>` (`crates/turborepo-boundaries/src/config.rs:39-46`), and the package-rule path in `check_package_tags` converts them to `ProcessedPermissions` and later reads `allow_list.span_and_text("turbo.json")` / `deny_list.span_and_text("turbo.json")` to build the secondary allow/deny diagnostics (`crates/turborepo-boundaries/src/tags.rs:403-420`, `crates/turborepo-boundaries/src/tags.rs:150-156`). Because no text/path was attached, those `Spanned` values have spans but no backing source text, so `NoTagInAllowlist` / `DeniedTag` diagnostics originating from package-level `boundaries.dependencies` or `boundaries.dependents` rules render without the expected `turbo.json` snippet, unlike diagnostics from tag rules (which work because `add_text` explicitly recurses into each `Rule`).

## Proposed regression test

Add a unit test in `crates/turborepo-boundaries/src/config.rs` (or the boundaries test module) that constructs a `BoundariesConfig` with populated `dependencies` and `dependents` permissions, calls `add_text`/`add_path`, and asserts that `config.dependencies.as_ref().unwrap().span_and_text("turbo.json")` and the same for `dependents` return both the original text and a path, rather than an empty `NamedSource`. For example:

```rust
#[test]
fn package_permissions_receive_source_metadata() {
    let mut config = BoundariesConfig {
        dependencies: Some(Spanned::new(Permissions {
            allow: Some(Spanned::new(vec![Spanned::new("@scope/allowed".into())])),
            deny: None,
        })),
        dependents: Some(Spanned::new(Permissions {
            allow: None,
            deny: Some(Spanned::new(vec![Spanned::new("@scope/denied".into())])),
        })),
        ..Default::default()
    };

    config.add_text(Arc::from(r#"{"dependencies":{"allow":["@scope/allowed"]}}"#));
    config.add_path(Arc::from("packages/app/turbo.json"));

    let (span, text) = config
        .dependencies
        .as_ref()
        .unwrap()
        .span_and_text("turbo.json");
    assert!(span.is_some());
    assert_eq!(text.inner().as_str(), r#"{"dependencies":{"allow":["@scope/allowed"]}}"#);
}
```

An integration variant should run the boundaries checker with an invalid package-level dependency rule and assert the emitted diagnostic's secondary `Allowlist`/`Denylist` source text is non-empty.

## Evidence

- `crates/turborepo-boundaries/src/config.rs:92-124` — `add_text`/`add_path` cover only `tags` and `implicit_dependencies`, omitting `dependencies` and `dependents`.
- `crates/turborepo-boundaries/src/config.rs:39-46` — package-level `dependencies` and `dependents` are `Spanned<Permissions>`, so they require the same metadata propagation as `tags`.
- `crates/turborepo-boundaries/src/tags.rs:403-420` and `crates/turborepo-boundaries/src/tags.rs:150-156` — package-level permissions are consumed and their `span_and_text("turbo.json")` output is used for allow/deny diagnostic source text, which is where the missing metadata surfaces.
