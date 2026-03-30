# 招商银行黄金行情 - 桌面悬浮窗

macOS 桌面悬浮窗应用，实时显示招商银行黄金价格，每 30 秒自动刷新。

---

## 功能特点

- 🪟 **无边框透明窗口** - 始终置顶显示
- 🎯 **智能透明度** - 鼠标离开时自动变为 30% 透明，悬停时恢复完整显示
- 🔄 **自动刷新** - 每 30 秒自动获取最新金价
- 🖱️ **可拖拽移动** - 通过顶部标题栏拖动窗口位置
- ⚡ **轻量级** - 基于 Electron + HTML5 构建

---

## 快速开始（macOS）

### 方式一：直接使用（推荐）

1. 前往 [Releases](https://github.com/H2Cat96/gold-desktop-float/releases) 下载对应 DMG
2. 双击 DMG，将「金价悬浮窗」拖入 Applications 文件夹
3. 首次打开：**右键应用 → 打开 → 在弹窗中点击「打开」**（绕过未签名提示）

| 文件 | 适用机型 |
|------|---------|
| `金价悬浮窗-x.x.x-arm64.dmg` | Apple M 芯片（M1/M2/M3/M4） |
| `金价悬浮窗-x.x.x.dmg` | Intel 芯片 |

### 方式二：从源码运行

```bash
cd desktop-float-gold
npm install
npm start
```

---

## 开发相关

### 打包 DMG 安装包

```bash
cd desktop-float-gold
npm install
npm run build
```

生成的 DMG 文件位于 `dist/` 目录。

### 项目结构

```
desktop-float-gold/
├── main.js           # Electron 主进程
├── preload.js        # 预加载脚本
├── index.html        # 前端界面
├── package.json      # 项目配置
└── build/            # DMG 打包配置和图标
```

---

## 数据来源

招商银行移动端接口：`https://m.cmbchina.com/api/rate/gold`

---

## 许可证

MIT

---

## 作者

RC-CHN, H2Cat96
