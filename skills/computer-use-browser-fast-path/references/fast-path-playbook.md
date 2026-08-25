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
