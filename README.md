# Twitter to Aria2 Downloader 🚀

一个简洁、高效的 Twitter/X 视频下载推送工具。通过 Web 界面解析 Twitter 视频链接，并一键推送到 Aria2 进行高速下载。

## ✨ 特性

- **多源解析**：集成 `fxtwitter` API 和 `yt-dlp` 双策略，确保解析成功率。
- **一键推送**：解析完成后自动调用 Aria2 RPC 接口，无需手动复制下载地址。
- **全家桶部署**：基于 Docker Compose，一键启动 Web 界面 + Aria2 服务。
- **适配性强**：支持通过环境变量配置代理、Aria2 令牌及地址。
- **响应式 UI**：基于 Bootstrap 5 构建，支持移动端访问。

## 🛠️ 快速开始

### 方式一：Docker Compose (推荐)

这是最简单的运行方式，会自动配置好 Web 服务和 Aria2 的相互通信。

1. **克隆仓库**
   ```bash
   git clone https://github.com/2653533859/twitter-aria-downloader.git
   cd twitter-aria-downloader
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **访问界面**
   打开浏览器访问 `http://localhost:5001`。

### 方式二：手动运行

如果你已有运行中的 Aria2 服务：

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **设置环境变量 (可选)**
   ```bash
   export ARIA2_RPC_URL="http://your-ip:6800/jsonrpc"
   export ARIA2_TOKEN="your-token"
   export PROXY="http://127.0.0.1:7890"
   ```

3. **运行**
   ```bash
   python app.py
   ```

## ⚙️ 环境变量说明

| 变量名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `ARIA2_RPC_URL` | `http://localhost:6800/jsonrpc` | Aria2 RPC 服务地址 |
| `ARIA2_TOKEN` | `nas123456` | Aria2 RPC 认证令牌 (RPC Secret) |
| `PROXY` | (空) | 网络代理地址，解析 Twitter 资源时必填 |

## 📦 项目结构

- `app.py`: Flask 后端逻辑
- `Dockerfile`: 应用镜像构建文件
- `docker-compose.yml`: 容器编排配置
- `downloads/`: (自动创建) Aria2 下载文件存放目录

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进本项目！

## 📄 开源协议

[MIT License](LICENSE)
