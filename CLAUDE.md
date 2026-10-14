# CLAUDE.md

本仓库是 Agent Skill「computer-use-browser-fast-path」：让 Agent 通过 Computer Use 操作浏览器时更快——初始化一次并复用持久会话、默认读可访问性文本、在状态边界之间批量执行确定动作、对稳定内循环做编译式重放，同时保留最终界面核验。它优化的是 Agent 与浏览器之间的往返，不让网站本身变快。用户只安装 `skills/computer-use-browser-fast-path/` 这一个目录。

## 目录

- `skills/computer-use-browser-fast-path/`：Skill 本体，会被复制到用户的 Skills 目录。
  - `SKILL.md`：Agent 使用说明（英文），frontmatter 的 `name` 必须是 `computer-use-browser-fast-path`。
  - `references/`：`fast-path-playbook.md`（`node_repl` / Computer Use 写法）、`benchmark.md`（可复现测速协议）、`douyin-image-post-prepublish.md`（停在发布按钮之前的真实案例）。
  - `scripts/` 下的 `check_update.py`：每 24 小时最多查一次 GitHub Latest Release，只提示不覆盖。
  - `agents/openai.yaml`：展示名、默认提示词和调用策略。
  - `VERSION`：发布版本号，只由维护者在发版时修改。
- `scripts/validate_repo.py`：仓库检查（Skill 结构、版本号、链接、文档引用路径、Python 语法、标签配置），不属于 Skill 流程。
- `tools/submit_feedback.py`：把社媒 / 社区反馈登记进 Issues，不属于 Skill 流程。
- `tests/`：`unittest` 测试。
- `.github/`：CI 与 Agent 工作流，见 `docs/agent-workflow.md`。
- `README.md`（中文）与 `README_EN.md`（英文）。

## 不可违背的原则

README「安全边界」与 `SKILL.md` 的 Scope boundary：

- 浏览器的读取和操作只通过 Computer Use，不改用或混用 Playwright、CDP、DOM 查询、注入 JavaScript、浏览器插件或浏览器专用 connector。
- 不绕过登录、验证码、浏览器安全警告、权限提示和风控 / 反滥用机制；不读取、导出或代填凭据。
- 速度不能替代授权：对外发布、上传、删除、购买等操作前的确认一个都不能省；抖音案例停在“发布”按钮之前。
- 页面变化后不复用旧的 `element_index`；“点击过”不等于成功，最终结果必须在浏览器界面中得到验证。
- 没有按 `benchmark.md` 做同任务、同环境的可复现测速，不写固定提速倍数。
- 更新检查只提示新版本，不自动下载或覆盖文件，联网失败静默继续，不关闭 TLS 校验。

代码和文档改动不能放宽这些边界，也不能放宽 `scripts/validate_repo.py` 的检查。

## 开发约定

- Python 3.10+，只用标准库，没有第三方依赖。
- 提交前必须通过：

  ```bash
  python scripts/validate_repo.py
  python -m unittest discover -s tests
  ```

- 行为改动配测试；测试不得真实联网（用 `mock` 或缓存文件），不依赖浏览器或 Computer Use 运行时。
- 用户可见变化同时同步 `README.md` 与 `README_EN.md`，必要时同步 `SKILL.md`。
- 新增参考文件放进 `references/`，在 `SKILL.md` 里用相对链接引用，并登记到 `scripts/validate_repo.py` 的 `REFERENCES`。
- 改版本号要同时改 `VERSION`、`scripts/validate_repo.py` 的 `VERSION` 和 `tests/test_check_update.py` 里的版本断言。
- 公开文件里不能出现本机绝对路径。
- 提交信息使用 `fix:` / `feat:` / `docs:` / `test:` / `ci:` 前缀，简体中文描述。
