---
name: computer-use-browser-fast-path
description: Accelerate browser workflows performed exclusively through Computer Use by reducing UI round trips, reusing a persistent session, batching deterministic actions, and verifying state boundaries. Use when the user asks to make browser Computer Use faster or run a browser workflow in fast mode; do not use for Playwright, CDP, DOM, browser-connector, or non-browser automation.
---

# Computer Use Browser Fast Path

Make browser work through Computer Use faster without weakening correctness, authorization, or final verification. This optimizes agent-to-UI round trips; it does not speed up the website itself.

## Scope boundary

- Perform every browser read and browser action through Computer Use. Do not switch to Playwright, CDP, DOM queries, injected JavaScript, browser extensions, or a browser-specific connector.
- Normal local preparation may use file or shell tools, but those tools must not control, inspect, or mutate the browser.
- Follow the current Computer Use confirmation policy. Speed never authorizes a consequential action or removes a required handoff.
- Do not bypass login challenges, CAPTCHAs, browser security warnings, permissions, or anti-abuse controls.

## Start

Run `python3 scripts/check_update.py` once near task start. Show its output only when it reports an update; never block the browser task if the check fails.

Before touching the UI, resolve the target browser, starting page, exact inputs, success condition, and the next action that may require confirmation. Prepare repeated text and local file paths before starting the timed browser sequence.

For the concrete `node_repl` and `@oai/sky` fast path, read [references/fast-path-playbook.md](references/fast-path-playbook.md).

## Fast-path loop

1. Initialize the Computer Use runtime once, target the known browser directly, and keep the session persistent.
2. Read one current state. Prefer accessibility text and the default diff behavior; inspect the screenshot only when the text is insufficient.
3. Classify the next actions as one atomic burst: every action must have a deterministic target and must not require observing an intermediate result.
4. Execute the burst. Use direct value setting and keyboard actions when the control supports them. Do not add arbitrary sleeps.
5. Read state once at the next meaningful boundary: navigation, modal open/close, upload completion, validation response, submission, or any layout change.
6. Derive fresh element indices from that state. Never reuse an index across a changed page.
7. Continue until the browser exposes evidence of the requested final result.

Keep bursts short when the site is dynamic. A burst ends before any branch, uncertain control, external mutation requiring confirmation, or action whose success affects the next target.

## Repeated workflows

Run the first item as calibration and record its stable route, required fields, boundaries, and final evidence. For later items, reuse that route but refresh state-derived indices after each boundary. Verify each item before advancing, and retain a checkpoint that prevents duplicate submission after interruption.

If two consecutive items diverge at the same boundary, leave fast mode and re-map the live workflow instead of accumulating retries.

## Recovery

On an unexpected state, stop the burst and request one fresh full state. If accessibility text still cannot explain the page, inspect the screenshot once. Retry only after identifying the cause and a changed action. Never repeat clicks, uploads, or submissions merely because the expected result is not yet visible.

## Completion

Report success only from current browser evidence: destination URL or view, visible status, item identity, count, time, or another task-specific invariant. Distinguish a submitted action from its later processing, review, or publication state.

Use [references/benchmark.md](references/benchmark.md) when evaluating or publicly claiming speed improvements.
