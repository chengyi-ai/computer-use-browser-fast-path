# Computer Use 快速路径

仅在实际控制浏览器时读取本文件。下面的例子面向 Codex 的持久 `node_repl` 与 `@oai/sky` Computer Use 接口。

## 1. 一次初始化

新会话只导入一次运行时，并直接使用已知浏览器标识：

```js
globalThis.sky = globalThis.sky ?? (await import("@oai/sky")).sky;
globalThis.browserApp = globalThis.browserApp ?? "com.google.Chrome";
globalThis.browserState = await sky.get_app_state({ app: browserApp });
nodeRepl.write(browserState.text);
```

不要为了确认 Chrome 标识先调用 `list_apps()`。只有直接定位失败时才列出应用，并在拿到 bundle identifier 后继续复用它。

## 2. 先读文本，按需看图

优先从 `browserState.text` 识别控件、当前值和 `element_index`。连续状态默认使用 diff，避免反复处理整棵可访问性树。

只有这些情况才展开截图：

- 可访问性文本缺少关键控件；
- 同名控件无法通过上下文区分；
- 需要判断画面、拖放位置、视觉选中态或非文本提示；
- 一次全量状态仍无法解释异常。

如果忽略过一次状态文本，下一次需要重新判断结构时使用全量状态：

```js
browserState = await sky.get_app_state({ app: browserApp, disableDiff: true });
nodeRepl.write(browserState.text);
```

## 3. 按状态边界分批

原子动作批次只包含无需查看中间结果就能确定执行的动作。例如，在同一稳定表单中填写两个字段：

```js
await sky.set_value({ app: browserApp, element_index: titleIndex, value: title });
await sky.set_value({ app: browserApp, element_index: bodyIndex, value: body });
browserState = await sky.get_app_state({ app: browserApp });
nodeRepl.write(browserState.text);
```

以下动作通常结束一个批次，随后重新读取状态：

- 地址跳转或页面导航；
- 打开、关闭弹窗或切换标签页；
- 文件上传开始或完成；
- 触发表单校验；
- 提交、发布、删除或其他外部状态变化；
- 页面重排、无限列表加载或控件索引可能变化。

不要跨状态边界复用旧 `element_index`。坐标也只在当前截图和窗口布局仍然成立时使用。

## 4. 选择最低往返的动作

- 可编辑控件优先 `set_value`，避免逐字模拟输入。
- 需要真实键盘语义时使用 `press_key`，例如 `Tab`、`Return`、`super+a`。
- 仅在控件不支持直接赋值时使用 `click` 后 `type_text`。
- `element_index` 优先于坐标；可访问性动作失效时再切换坐标。
- 一次输入完整字符串；不要按字符拆成多次调用。
- 不主动插入固定延迟。动作后的 `get_app_state` 会让运行时处理普通界面稳定等待。

`type_text` 中的换行可能提交表单。含 `\n` 或 `\r` 的文本必须先确认目标编辑器会插入换行，而不是发送内容。

## 5. 批量任务的黄金路径

第一条任务用于校准，不用于猜测：

1. 确认起点、账号、输入与最终证据；
2. 识别所有状态边界；
3. 跑通并核验第一条；
4. 记录稳定步骤和可变字段；
5. 从第二条开始复用步骤，但每次页面变化后刷新索引。

每条成功后保存最小检查点，例如条目编号、标题、目标时间和页面状态。恢复时先在 UI 中核验最后一条，再从下一条继续。

## 6. 有界恢复

第一次异常：停止动作并读取全量状态。

第二步仍不明确：查看当前截图，定位遮挡、弹窗、加载或布局变化。

只有原因明确且下一步不同于失败动作时才重试。若同一边界连续两次失败，退出快速路径并重新映射当前页面；不要继续盲点。

## 7. 把稳定内循环编译到一次 `node_repl` 调用

已经跑通的重复步骤可以保留必要的 UI 状态读取，同时减少模型与工具之间的往返。做法是把一个无语义分支的内循环写成持久 `node_repl` 函数：每个动作边界仍调用 `get_app_state`，但在同一次 JavaScript 执行里从最新可访问性文本解析下一个控件索引。

```js
function findIndex(text, label) {
  for (const line of text.split("\n")) {
    if (!line.includes(label)) continue;
    const match = line.match(/(?:^|\t)(\d+)\s+/);
    if (match) return Number(match[1]);
  }
  return null;
}

async function runStableStep(startIndex, value) {
  await sky.click({ app: browserApp, element_index: startIndex });
  await sky.get_app_state({ app: browserApp });
  await sky.paste({ app: browserApp, text: value, format: "text" });
  const state = await sky.get_app_state({ app: browserApp });
  const nextIndex = findIndex(state.text, "下一步的稳定标签");
  if (nextIndex == null) throw new Error("稳定路径失效，退出快速模式");
  return { state, nextIndex };
}
```

只编译满足这些条件的区间：

- 输入、目标控件和成功条件都已由黄金路径验证；
- 中间页面不会要求用户判断、授权或选择不确定候选；
- 每次页面变化后都从新状态计算索引；
- 找不到控件或断言不成立时立即抛错并退出，不提供兜底坐标乱点；
- 提交、发布、删除、购买等后果动作仍停在确认边界之外。

区分两个指标：`state_reads` 是 Computer Use 对界面的必要观察次数；`model_round_trips` 是模型与工具之间的往返次数。编译式重放主要减少后者，不应为了压低前者而跨过动态状态。

## 8. 富文本与结构化实体

标签、话题、提及、商品卡等通常不是普通文本。若平台要求从候选面板激活，粘贴可见的 `#标签` 不等于创建结构化实体。

- 在创建任何结构化实体之前，一次性写入完整正文并核对末句；不要在实体创建后继续做长正文的光标手术。
- 空编辑器优先一次 `set_value` 写入正文。若编辑器已有 Slate 等富文本节点，先清空、重新读取状态，再写入正文。
- `select_text`、`End` 或坐标在长富文本里无法稳定落点时，不要补丁式修复；重置正文并重放结构化实体通常更快、更可靠。
- 每个实体都从平台候选中确认，并在最终预览或可访问性结构中核对数量和文本。

## 9. macOS 文件选择器快路径

本地准备可以使用文件或 shell 工具，但不能借此控制浏览器。遇到中文或很长的本地路径时，可在定时段开始前创建指向素材目录的临时 ASCII 路径；不要改名或移动源文件。

推荐顺序：

1. 点击上传并进入文件选择器；
2. 确认浏览器仍在前台；若通知或其他应用抢到焦点，先重新读取浏览器状态并显式聚焦；
3. 用“前往文件夹”打开临时 ASCII 路径；输入框可能保留上次路径，应先全选或三击清空，再输入新路径；
4. 切换列表视图，并用点击第一行或一次 `Down` 明确选中第一项；两种方式只选一种；
5. 对剩余连续文件使用 `Shift+Down` 批量选择；8 个文件应是第一项加 7 次 `Shift+Down`；
6. 确认“打开”按钮已启用后点击，随后在网页状态中核对实际上传数量；
7. 数量少于预期时立即停止后续填写，补齐缺失文件并重新核对；
8. 上传完成后清理临时路径。

若文件选择器不能可靠接收粘贴，ASCII 路径可用 `type_text`；中文路径不要依赖逐字模拟。前往文件夹不可用时，再退回列表视图和可访问性“打开项目”动作逐级导航。

不要在同一编译式动作串里连续执行多个剪贴板粘贴。系统剪贴板恢复与应用读取可能竞争，导致旧剪贴板内容进入表单。长正文可单独粘贴并立即核对；短标签或路径优先用 `type_text`。

页面滚动前先确认焦点不在 Slate 编辑器、文件列表或其他内部滚动容器。若滚动只移动了内部内容，点击一个已知空白页区后再滚动整页。
