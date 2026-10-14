# Computer Use Browser Fast Path

An open-source Agent Skill for making browser workflows feel faster while keeping every browser interaction inside Computer Use.

It does not use Playwright, CDP, DOM injection, browser extensions, or in-page scripts. The speedup comes from reducing redundant perception round trips, reusing one persistent session, and grouping deterministic actions between verifiable UI state boundaries.

This Skill reduces agent-to-browser overhead. It cannot accelerate the website's network, backend, or rendering performance.

## What it changes

- Initialize the Computer Use runtime once and reuse the same browser session.
- Target a known browser directly instead of listing every app first.
- Read accessibility text and state diffs by default; inspect screenshots only when needed.
- Group deterministic field and keyboard actions while the layout remains stable.
- Re-read state at navigation, modal, upload, submit, and other meaningful boundaries.
- Avoid arbitrary sleeps; use the runtime's built-in UI settling behavior.
- Calibrate one golden item before repeating a batch, while refreshing element indices for every changed page.
- Compile a verified inner loop into one persistent `node_repl` call so actions, state reads, and fresh-index parsing stay together without skipping UI checks.
- Recover with one full state read and then a screenshot instead of blind retries.

## Boundaries

Fast mode never bypasses authorization, confirmations, login challenges, security warnings, or final verification. It never reuses stale element indices after the page changes, and it does not claim a fixed speed multiplier without a controlled benchmark.

## Install

Ask Codex `$skill-installer` to install:

```text
https://github.com/chengyi-ai/computer-use-browser-fast-path/tree/main/skills/computer-use-browser-fast-path
```

Or install manually:

```bash
git clone https://github.com/chengyi-ai/computer-use-browser-fast-path.git
mkdir -p ~/.codex/skills
cp -R computer-use-browser-fast-path/skills/computer-use-browser-fast-path ~/.codex/skills/
```

## Use

```text
Use $computer-use-browser-fast-path to complete this workflow in my logged-in Chrome. Keep every browser interaction inside Computer Use, use the fast path, and verify the final UI state.
```

See the [benchmark protocol](skills/computer-use-browser-fast-path/references/benchmark.md) before publishing speed claims.

The repository also includes a real [Douyin image-post pre-publish case study](skills/computer-use-browser-fast-path/references/douyin-image-post-prepublish.md) covering macOS file selection, Slate rich text, and structured-topic replay without clicking Publish.

## Feedback

If the fast path fails, slows down, or you have an idea for a faster workflow, [open an issue](https://github.com/chengyi-ai/computer-use-browser-fast-path/issues/new/choose). Include the browser, the agent you used, and the step that went wrong. **Do not paste passwords, cookies, tokens, or other account data**, and redact screenshots.

An agent reads the code, assesses feasibility, and replies on the issue with a verdict and a plan. Once a maintainer approves, the agent edits the docs or code, runs the tests, and opens a pull request; a human always reviews before merging. Requests to bypass logins, CAPTCHAs, anti-abuse controls, or confirmations will not be accepted. See [docs/agent-workflow.md](docs/agent-workflow.md) (Chinese) for the full workflow and setup.

## License

[MIT](LICENSE)
