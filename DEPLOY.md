# GitHub 主页部署文档

`chenzk6` 个人主页（`chenzk6/chenzk6` 仓库的 README）是一套**自托管 SVG 卡片设计系统**：纯静态 + GitHub Actions 定时生成，无后端、无成本。

## 架构

- 每张卡片是脚本生成的 `.svg`，托管在仓库 `assets/`，README 用 `<picture>` 引用 `raw.githubusercontent.com` 加载。
- 每张卡片生成亮色 `xxx.svg` + 暗色 `xxx-dark.svg`，`<picture>` 用 `<source media="(prefers-color-scheme: dark)">` 自动切换。
- 数据来源：GitHub REST API（`GITHUB_TOKEN` 提限额）、open-meteo 天气、`Platane/snk` 贪吃蛇。
- GitHub Actions 按 cron 定时重跑 → 提交回 `main`。

## 目录结构

```
chenzk6/
├── README.md                        # 主页，<picture> 卡片堆叠
├── .github/
│   ├── scripts/
│   │   ├── build_assets.py          # banner/typing/journey/projects/clock/stats
│   │   └── weather.py               # weather（杭州天气）
│   └── workflows/generate.yml       # 定时 + push 触发生成
└── assets/                          # 16 个 SVG（8 卡片 × 明暗）
```

## 部署步骤

1. 推送代码到 `chenzk6/chenzk6` 的 `main`：

   ```bash
   git add README.md .github assets
   git commit -m "deploy: profile SVG cards"
   git push
   ```

2. 推送会触发 `generate.yml`（`push` 触发器）自动生成全部 SVG 并提交一次。
3. 等 1~2 分钟，刷新个人主页即可。主页只引用 `raw.githubusercontent.com` 的 `assets/*.svg`，无需开启 Pages。

## 配置

改 [.github/scripts/build_assets.py](.github/scripts/build_assets.py) 顶部常量：

| 常量 | 含义 |
|---|---|
| `USERNAME` | GitHub 用户名 |
| `TAGLINE` | banner 一句定位语 |
| `TYPING_LINES` | 打字机循环的两句英文 |
| `LINKS` | 展示的链接（email / scholar / website） |
| `PINNED_REPOS` | 项目卡固定仓库名，留空则自动按 star 选 top4 |
| `THEMES` | 亮/暗色板（accent 绿色可改） |

天气城市改 [.github/scripts/weather.py](.github/scripts/weather.py) 顶部 `LAT, LON`（当前杭州）。改完 push，Actions 自动重新生成。

## 自动化

`generate.yml`：`push` 到 main + cron `17 */6 * * *` + 手动触发，`permissions: contents: write`。

Workflow 用自带 `GITHUB_TOKEN` 提交不会再次触发 push，因此不会死循环。

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 卡片「还是没变」 | raw CDN 缓存 | 强制刷新（Ctrl+F5）/ 无痕 |
| 本地 push 报 443 超时 | 到 github.com 网络波动 | 重试；最终更新交给 Actions |
| stats 数字为 0 | 生成时 API 失败 | 手动触发 `generate.yml` 重跑 |
| workflow 不运行 | 缺 push 触发 / 权限不足 | 确认 `on:` 含 `push`、`permissions: contents: write` |

## 本地调试

```bash
python .github/scripts/build_assets.py   # 生成卡片（需访问 api.github.com）
python .github/scripts/weather.py        # 生成天气卡（纯 stdlib）

gh workflow run generate.yml -R chenzk6/chenzk6   # 手动触发线上更新
```
