# Computer Use Browser Fast Path

一个专门优化 **Computer Use 操作浏览器速度** 的开源 Agent Skill。

它不调用 Playwright、CDP、DOM 注入、浏览器插件或网页脚本。所有浏览器点击、输入、滚动、快捷键和页面读取仍由 Computer Use 完成；提速来自减少无效观察轮次、复用持久会话，并把无分支动作合并成可验证的小批次。

> 这个 Skill 优化的是 Agent 与浏览器之间的交互往返，不会让网站网络、服务器或页面渲染本身变快。

## 核心提速方法

- Computer Use 运行时只初始化一次，并持续复用同一个浏览器会话；
- 已知浏览器时直接使用应用标识，不先扫描全部应用；
- 默认读取可访问性文本和增量状态，只在信息不足时查看完整截图；
- 在布局不变、结果确定的区间内批量执行输入和快捷键；
- 只在导航、弹窗、提交、上传完成等“状态边界”重新读取页面；
- 不添加固定 `sleep`，让 Computer Use 自带的界面等待机制处理普通加载；
- 批量工作先跑通一条“黄金路径”，后续条目复用路径但始终刷新元素索引；
- 出错时先读取一次全量状态，再按需查看截图，不连续盲点或重复提交。

## 安全边界

速度不能越过授权、确认和核验：

- 不绕过登录、验证码、安全警告或权限提示；
- 不因追求速度而跳过对外发布、上传、删除、购买等操作所需的确认；
- 不在页面变化后复用旧的 `element_index`；
- 不把“点击过”当成成功，最终结果必须在浏览器界面中得到验证；
- 不声称固定提速倍数，除非在同一任务、同一环境中完成了可复现测速。

## 仓库结构

```text
skills/computer-use-browser-fast-path/
├── SKILL.md
├── VERSION
├── agents/openai.yaml
├── references/fast-path-playbook.md
├── references/benchmark.md
└── scripts/check_update.py
```

## 安装

### Codex Skill Installer

在 Codex 中调用 `$skill-installer`，安装下面的 Skill 目录：

```text
https://github.com/chengyi-ai/computer-use-browser-fast-path/tree/main/skills/computer-use-browser-fast-path
```

### 手动安装

```bash
git clone https://github.com/chengyi-ai/computer-use-browser-fast-path.git
mkdir -p ~/.codex/skills
cp -R computer-use-browser-fast-path/skills/computer-use-browser-fast-path ~/.codex/skills/
```

重新打开 Codex 任务后即可使用。

## 使用示例

```text
使用 $computer-use-browser-fast-path，只通过 Computer Use 在我已登录的 Chrome 中完成这个网页流程，优先走快速路径，并在最终状态做核验。
```

对于批量网页工作流：

```text
使用 $computer-use-browser-fast-path 先跑通第一条并建立黄金路径，再处理剩余条目。浏览器操作只能用 Computer Use；遇到页面结构变化就退出快速路径重新读取状态。
```

## 如何判断真的变快

不要只看鼠标移动快不快。应同时记录总耗时、状态读取次数、截图展开次数、重复动作和最终是否正确。详见 [测速协议](skills/computer-use-browser-fast-path/references/benchmark.md)。

## 更新策略

Skill 最多每 24 小时检查一次 GitHub Latest Release。它只提示新版本，不会自动覆盖本地文件；断网或 GitHub 不可用时会静默继续当前任务。

## License

[MIT](LICENSE)
