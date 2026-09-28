# 🍽️ 校园美食规划助手

**Agentic App 黑客松 2026 参赛作品**

> 用 AI 帮你规划一周校园美食，自动生成营养均衡的菜谱和采购清单

---

## 📋 项目概述

| 项目 | 说明 |
|------|------|
| **场景** | 校园生活 |
| **目标用户** | 大学生、校园周边商家 |
| **核心功能** | AI 菜谱规划 + 智能采购清单 |
| **技术栈** | OctoSense + Makepad + Octoscript + Rust |

---

## ✨ 功能特点

| 功能 | 说明 |
|------|------|
| 🎯 智能偏好 | 8 种口味标签自由组合 |
| 🤖 AI 规划 | Agent 自动分析、匹配、生成 |
| 📊 营养统计 | 热量/蛋白质/菜品数一目了然 |
| 🛒 采购清单 | 自动计算用量，可勾选 |
| 📱 多平台 | Android/iOS/macOS/Windows/Linux/Web |
| 🍳 真实数据 | 校园食堂菜单数据库 |

---

## 📁 项目结构

```
campus-meal-planner/
├── bundle/                    # OctoSense 应用包（提交内容）
│   ├── manifest.json         # 权限配置
│   ├── listing.json          # 商店展示
│   ├── main.splash           # 应用代码
│   ├── assets/               # 图标等资源
│   └── screenshots/          # 真实截图
├── src/                       # Rust 后端
│   ├── main.rs               # 主程序
│   ├── algorithm.rs          # 菜谱算法
│   ├── data.rs               # 数据处理
│   ├── scraper.rs            # 菜单爬取
│   └── html.rs               # HTML 生成
├── menus/                     # 菜单数据
├── docs/                      # 文档
│   ├── BRIEF.md              # 任务说明
│   ├── AGENT-TASKS.md        # Agent 任务
│   └── DEMO.md               # 演示说明
├── demo/                      # 演示材料
├── build/                     # 构建产物
├── all_menus.json             # 完整菜单数据
├── menu.csv                   # 菜单 CSV
├── products_clean.json        # 商品数据
├── meal_plan_*.csv            # 菜谱计划
└── README.md                  # 本文件
```

---

## 🚀 快速开始

### 运行 OctoSense 应用

```bash
# 进入开发环境
cd /home/windy/Project/octosense-ws/OctoScript-App-Design-Flow

# 运行应用
tools/octo run /home/windy/Project/campus-meal-planner/bundle --port 8150 --detach

# 测试交互
curl -s 127.0.0.1:8150/snap                    # 查看 UI
curl -s "127.0.0.1:8150/click?x=62&y=469&wait=1"  # 点击按钮

# 截图
tools/octo shot 8150 screenshot.png

# 退出
curl -s 127.0.0.1:8150/quit
```

### 运行 Rust 后端

```bash
cd /home/windy/Project/campus-meal-planner
cargo run
```

### 检查应用

```bash
tools/octo check /home/windy/Project/campus-meal-planner/bundle
```

---

## 🎯 场景说明

### 痛点分析

| 问题 | 现状 | 影响 |
|------|------|------|
| 不知道吃什么 | 每天纠结，浪费时间 | 体验差 |
| 营养不均衡 | 随意搭配，不健康 | 身体影响 |
| 采购靠手写 | 容易遗漏，重复买 | 效率低 |
| 预算难控制 | 花钱没计划 | 经济压力 |

### 解决方案

```
用户选择偏好
     ↓
AI 分析营养需求
     ↓
生成菜谱计划
     ↓
计算采购清单
     ↓
用户执行采购
```

---

## 🤖 Agent 自动化

| 步骤 | Agent 任务 | 用户操作 | 验证点 |
|------|-----------|---------|--------|
| 1 | - | 选择偏好标签 | 立即反馈 |
| 2 | 分析偏好 | - | 加载动画 |
| 3 | 匹配营养 | - | 进度显示 |
| 4 | 生成菜谱 | - | 菜谱展示 |
| 5 | 计算采购 | - | 清单展示 |
| 6 | - | 勾选采购项 | 交互反馈 |

---

## 📊 数据说明

### 菜单数据

| 文件 | 内容 | 记录数 |
|------|------|--------|
| `all_menus.json` | 完整菜单 | 1000+ |
| `menu.csv` | 菜单 CSV | 500+ |
| `products_clean.json` | 商品数据 | 300+ |

### 菜谱计划

| 文件 | 类型 | 菜品数 |
|------|------|--------|
| `meal_plan_A1.csv` | 计划 A | 3 |
| `meal_plan_A2.csv` | 计划 B | 3 |
| `meal_plan_A3.csv` | 计划 C | 3 |

---

## 🎨 界面预览

### 欢迎页

```
┌─────────────────────────────────┐
│  🍽️ 美食规划                     │
├─────────────────────────────────┤
│  👋 欢迎使用                      │
│  智能美食规划                     │
│                                 │
│  选择你的偏好                    │
│  [🥬清淡] [🌶️微辣]              │
│  [🍖高蛋白] [🥗健康]            │
│  ...                            │
│                                 │
│  [✨ 开始规划]                  │
└─────────────────────────────────┘
```

### 结果页

```
┌─────────────────────────────────┐
│  🍽️ 美食规划                     │
├─────────────────────────────────┤
│  🔥 1850    💪 85g    ⭐ 3道     │
├─────────────────────────────────┤
│  📋 今日推荐                     │
│  🌅 早餐: 牛油果吐司             │
│  ☀️ 午餐: 藜麦沙拉               │
│  🌙 晚餐: 清蒸鲈鱼               │
├─────────────────────────────────┤
│  🛒 采购清单                     │
│  [✓] 鸡蛋 (10个)                │
│  [ ] 鸡胸肉 (500g)              │
└─────────────────────────────────┘
```

---

## 📝 提交材料

### 必须提交

- [x] 源码仓库（Apache 2.0）
- [x] 可运行版本
- [x] 任务说明 (`docs/BRIEF.md`)
- [x] Agent 任务演示 (`docs/AGENT-TASKS.md`)
- [x] 真实截图
- [x] 数据来源说明

### 补充材料

- [ ] 演示视频（2-3分钟）
- [ ] 用户测试记录
- [ ] 失败状态截图

---

## 🔧 技术实现

### 前端 (OctoSense)

```splash
// 应用入口
let preferences = []
let shoppingList = []

fn start_planning(){
    // Agent 任务
    step = 1
    ui.main.render()
    
    // 生成菜谱
    start_timeout(1.2, || {
        step = 3
        ui.main.render()
    })
}
```

### 后端 (Rust)

```rust
// 菜谱算法
fn generate_meal_plan(preferences: Vec<String>) -> MealPlan {
    // 1. 分析偏好
    // 2. 匹配营养
    // 3. 生成菜谱
    // 4. 计算采购
}
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [BRIEF.md](docs/BRIEF.md) | 任务说明、完成标准 |
| [AGENT-TASKS.md](docs/AGENT-TASKS.md) | Agent 任务演示 |
| [DEMO.md](docs/DEMO.md) | 演示脚本 |

---

## 📄 许可证

Apache License 2.0

---

## 🙏 致谢

- [OctoSense](https://github.com/OctoSense-org) - 应用框架
- [Makepad](https://github.com/OctoSense-org/makepad) - UI 渲染
- [Octoscript](https://github.com/OctoSense-org/Octoscript) - 开发语言
- [Agentic App Hackathon](https://create.gosim.org/agenticapp26/) - 比赛平台
