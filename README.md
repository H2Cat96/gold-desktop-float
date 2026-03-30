# 招商银行黄金行情插件

实时查询招商银行黄金价格，支持 [AstrBot](https://github.com/Soulter/AstrBot) 聊天机器人插件与 macOS 桌面悬浮窗两种使用方式。

---

## 功能一：AstrBot 插件

在 AstrBot 中发送 `/gold` 指令，即可获取最新黄金行情（品种、当前价、涨跌幅、最高/最低价）。

### 安装

将本仓库克隆/下载后，放入 AstrBot 插件目录，重启 AstrBot 即可。

### 使用

```
/gold
```

返回示例：

```
=== 招商银行黄金行情 ===
更新时间: 2025-01-01 10:00:00

品种: 人民币黄金
当前价: 625.00
涨跌幅: +1.23%
最高价: 626.00
最低价: 620.00
```

### 依赖

- AstrBot
- aiohttp（AstrBot 环境自带）

---

## 功能二：macOS 桌面悬浮窗

基于 Electron 构建的桌面端悬浮窗，始终置顶显示实时金价，每 30 秒自动刷新。

📁 源码位于 [`desktop-float-gold/`](./desktop-float-gold/) 目录，详见其 [README](./desktop-float-gold/README.md)。

### 快速使用（macOS）

1. 前往 [Releases](https://github.com/RC-CHN/astrbot-gold-plugin/releases) 下载对应 DMG
2. 双击 DMG，将「金价悬浮窗」拖入 Applications 文件夹
3. 首次打开：**右键应用 → 打开 → 在弹窗中点击「打开」**（绕过未签名提示）

| 文件 | 适用机型 |
|------|---------|
| `金价悬浮窗-x.x.x-arm64.dmg` | Apple M 芯片（M1/M2/M3/M4） |
| `金价悬浮窗-x.x.x.dmg` | Intel 芯片 |

### 悬浮窗功能

- 始终置顶、无边框透明窗口
- 鼠标离开时自动变为 30% 透明，悬停时恢复完整显示
- 顶部标题栏可拖拽移动窗口
- 支持手动刷新

---

## 数据来源

招商银行移动端接口：`https://m.cmbchina.com/api/rate/gold`

---

## 作者

RC-CHN
