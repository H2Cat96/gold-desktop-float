# 金价桌面悬浮窗（Electron）

基于招商银行黄金行情接口构建的 macOS 桌面悬浮窗。

## 功能

- 始终置顶、无边框、透明可拖拽悬浮窗口
- 实时拉取招商银行黄金行情（数据源：`https://m.cmbchina.com/api/rate/gold`）
- 每 30 秒自动刷新，支持手动刷新
- 鼠标离开时自动变为 30% 透明，悬停时恢复完整显示
- 可选 HTTP/HTTPS 代理（读取环境变量 `HTTP_PROXY` / `http_proxy`）

---

## 普通用户：直接下载安装包

前往 [Releases](https://github.com/RC-CHN/astrbot-gold-plugin/releases) 下载对应 DMG：

| 文件 | 适用机型 |
|------|---------|
| `金价悬浮窗-x.x.x-arm64.dmg` | Apple M 芯片（M1/M2/M3/M4） |
| `金价悬浮窗-x.x.x.dmg` | Intel 芯片 |

**首次打开提示"无法验证开发者"时**：右键应用 → 打开 → 在弹窗中点「打开」，之后正常双击即可。

---

## 开发者：本地运行

### 环境要求

- Node.js 18+
- npm 9+

### 安装与启动

```bash
cd desktop-float-gold
npm install
npm start
```

### 使用代理（可选）

```bash
export HTTP_PROXY="http://127.0.0.1:7890"
npm start
```

---

## 开发者：打包 DMG

```bash
cd desktop-float-gold
npm install
npm run build
```

输出文件在 `dist/` 目录：
- `金价悬浮窗-x.x.x-arm64.dmg`（Apple Silicon）
- `金价悬浮窗-x.x.x.dmg`（Intel x64）

---

## 文件结构

```
desktop-float-gold/
├── main.js          # 主进程：创建无边框置顶窗口，处理透明度事件
├── preload.cjs      # 安全桥接：在隔离上下文中拉取招商银行接口
├── index.html       # 渲染进程 UI：行情展示与定时刷新逻辑
├── build/
│   ├── AppIcon.icns       # 应用图标
│   └── dmg_background.png # DMG 安装界面背景
└── package.json
```
