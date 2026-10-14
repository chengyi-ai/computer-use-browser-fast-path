## 改动内容

<!-- 解决了什么问题，改了哪些文件。关联 issue：Closes #N -->

## 测试

- [ ] `python scripts/validate_repo.py`
- [ ] `python -m unittest discover -s tests`
- [ ] 行为改动已补测试（测试不真实联网）
- [ ] 用户可见变化已同步 `README.md`、`README_EN.md`，必要时同步 `SKILL.md`
- [ ] 改了快速路径指引的，已在真实浏览器里验证，或在下面写明待验证的点

## 安全边界

- [ ] 浏览器读写仍只通过 Computer Use
- [ ] 没有绕过登录、验证码、安全警告、权限提示或风控，没有跳过对外操作前的确认
- [ ] 新增的速度结论有可复现测速支撑（没有则不写）

## 风险与回滚
