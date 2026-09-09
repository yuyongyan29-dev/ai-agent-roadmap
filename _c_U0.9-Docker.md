# U0.9 · Docker（6 小时）

**这个单元解决什么问题**

「在我机器上能跑」是软件行业最有名的一句借口。Docker 让这句话作废——**把你的程序连同它需要的操作系统、Python 版本、系统库、依赖包，全部打包成一个镜像**，在任何装了 Docker 的机器上跑出完全一样的结果。

对你的直接价值有三个：不用在本机装一堆数据库和中间件；S4 部署时直接把镜像推上去；S6 做 Agent 沙箱时，容器就是隔离的基础。

**学完你能做到**：把你的服务打包成镜像，用一条命令同时启动服务和数据库。

---

## 步骤 1 · 装 Docker 并跑第一个容器

### 这一步在做什么

装好，然后用一条命令启动一个别人做好的程序。

### 怎么做

装 [OrbStack](https://orbstack.dev/)（Mac 上比 Docker Desktop 更轻更快，命令完全一样）：

```bash
brew install --cask orbstack
```

或者装官方的 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

装完打开应用，验证：

```bash
docker --version
docker run hello-world
```

**跑一个真的数据库试试**：

```bash
docker run --name pg -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:17
```

拆解这条命令：

| 部分 | 含义 |
|---|---|
| `run` | 创建并启动一个容器 |
| `--name pg` | 给容器起个名字，方便后面引用 |
| `-e POSTGRES_PASSWORD=dev` | 设置环境变量 |
| `-p 5432:5432` | **端口映射**：把容器的 5432 端口映射到你电脑的 5432 |
| `-d` | 后台运行（detached） |
| `postgres:17` | 用哪个镜像，冒号后是版本标签 |

**注意你没有装 Postgres**，但现在你电脑上就有一个能用的 Postgres 了。

常用命令：

```bash
docker ps                    # 看正在运行的容器
docker ps -a                 # 看所有容器（包括停止的）
docker logs pg               # 看日志
docker logs -f pg            # 持续跟踪日志
docker exec -it pg psql -U postgres    # 进容器里执行命令
docker stop pg               # 停止
docker start pg              # 重新启动
docker rm pg                 # 删除（要先 stop）
docker images                # 看本地有哪些镜像
```

### 可能卡在哪

**`Cannot connect to the Docker daemon`**

Docker 应用没启动。打开 OrbStack 或 Docker Desktop 应用。

**`port is already allocated`**

5432 端口被占用了——很可能是 U0.8 装的本地 Postgres 还在跑。

两个选择：停掉本地的（`brew services stop postgresql@17`），或者换个端口映射（`-p 5433:5432`，然后连接时用 5433）。

**下载镜像特别慢**

Docker Hub 在国外。配国内镜像加速：OrbStack 或 Docker Desktop 的设置里找 Docker Engine 配置，加上 `registry-mirrors`。

**容器一启动就退出**

`docker ps` 看不到，`docker ps -a` 显示 `Exited`。用 `docker logs 容器名` 看为什么退出——通常是配置错误或者缺环境变量。

### 背后的逻辑

**容器和虚拟机的区别**

虚拟机是模拟一整台电脑，包括完整的操作系统内核。启动要几十秒，占几个 GB。

容器**共享宿主机的内核**，只打包应用和它需要的用户态文件。启动几百毫秒，占几十到几百 MB。

实现原理是 Linux 的两个内核特性：

- **namespace**：让容器看到的进程、网络、文件系统是「自己的一套」
- **cgroups**：限制容器能用多少 CPU、内存

**所以容器本质上就是一个被隔离和限制了的普通进程。** 它不是一台虚拟的电脑。

（Mac 上没有 Linux 内核，所以 Docker Desktop / OrbStack 实际上跑了一个轻量 Linux 虚拟机，容器在里面。这是为什么 Mac 上偶尔会遇到文件性能问题。）

**理解「容器不是完整隔离」这一点，在 S6 做 Agent 沙箱时至关重要**——容器的隔离性对付误操作够用，对付蓄意攻击就不一定够。

---

## 步骤 2 · 写 Dockerfile

### 这一步在做什么

写一个「配方」，告诉 Docker 怎么把你的项目做成镜像。

### 怎么做

在 `s0-foundation/csvstats/` 建 `Dockerfile`：

```dockerfile
FROM python:3.13-slim

# 装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 先只拷依赖声明，单独装依赖
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# 再拷代码
COPY src/ ./src/
RUN uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "csvstats.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

逐条解释：

| 指令 | 作用 |
|---|---|
| `FROM` | 基于哪个镜像开始。`slim` 是精简版，体积小很多 |
| `COPY --from=` | 从另一个镜像里拷文件过来，这是装 uv 的官方推荐方式 |
| `WORKDIR` | 设置工作目录，后续命令都在这里执行 |
| `COPY` | 把宿主机的文件拷进镜像 |
| `RUN` | 构建镜像时执行命令 |
| `EXPOSE` | 声明容器监听哪个端口（**只是文档作用，不会真的开放**） |
| `CMD` | 容器启动时执行什么 |

构建并运行：

```bash
docker build -t csvstats:dev .
docker run -p 8000:8000 csvstats:dev
```

访问 http://127.0.0.1:8000/docs。

### 为什么要分两次 COPY

**这是 Dockerfile 最重要的优化技巧。**

Docker 构建时每条指令生成一「层」，并且**会缓存**。下次构建时，如果某一层的输入没变，就直接用缓存。

所以：

```dockerfile
COPY pyproject.toml uv.lock ./     # 依赖声明变了才重新装依赖
RUN uv sync --frozen --no-install-project
COPY src/ ./src/                   # 只改代码时，从这一层才开始重建
```

如果写成 `COPY . .` 然后 `RUN uv sync`，**你每改一行代码，都要重装全部依赖**，构建从 5 秒变成 3 分钟。

### 可能卡在哪

**`--host 0.0.0.0` 不能省**

容器里如果 uvicorn 监听 `127.0.0.1`，它只接受容器**内部**的连接，你从外面访问不到。必须监听 `0.0.0.0`（所有网卡）。

**这是 Docker 新手最常见的「服务起来了但访问不了」的原因。**

**镜像特别大**

- 用 `slim` 或 `alpine` 基础镜像
- 写 `.dockerignore`，别把 `.venv`、`.git`、测试数据拷进去
- 用多阶段构建：一个阶段装编译工具和依赖，另一个阶段只拷结果

**改了代码但容器里还是旧的**

`docker build` 会用缓存。确认你的 `COPY src/` 在依赖安装之后。实在不行 `docker build --no-cache`。

**`.dockerignore` 要写什么**

```
.venv/
.git/
__pycache__/
*.pyc
.pytest_cache/
tests/
.env
```

**`.env` 一定要写进去** —— 密钥绝不能打包进镜像。

### 背后的逻辑

**镜像是分层的、只读的。**

每条 Dockerfile 指令生成一层，层之间是叠加关系。容器运行时，在所有只读层之上加一个可写层。

这个设计带来两个重要后果：

1. **多个容器可以共享同一批只读层**，所以启动 10 个相同镜像的容器，磁盘上只有一份
2. **容器里的改动是临时的**。容器删掉，可写层就没了。**所以数据必须存在容器外面**——这就是下一步的「卷」

---

## 步骤 3 · Compose：一条命令起全套

### 这一步在做什么

你的服务需要数据库，数据库需要先启动，两者要能互相访问。手动 `docker run` 两次太麻烦，用 Compose 声明一次。

### 怎么做

在项目根目录建 `compose.yaml`：

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: csvstats
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 3s
      timeout: 3s
      retries: 20

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+psycopg://app:dev@db:5432/csvstats
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src          # 开发时挂载代码，改了立刻生效

volumes:
  pgdata:
```

启动：

```bash
docker compose up            # 前台运行，能看到日志
docker compose up -d         # 后台运行
docker compose logs -f api   # 看某个服务的日志
docker compose down          # 停止并删除容器
docker compose down -v       # 连同数据卷一起删（数据全没）
```

### 三个关键点

**一、容器之间用服务名互相访问**

注意 `DATABASE_URL` 里写的是 `@db:5432` 而不是 `localhost`。

Compose 会创建一个内部网络，**服务名就是主机名**。`api` 容器里访问 `db` 这个名字，就能连到数据库容器。

`localhost` 在容器里指的是容器自己，连不上别的容器。**这是新手第二常见的坑。**

**二、卷（volumes）让数据活下来**

```yaml
volumes:
  - pgdata:/var/lib/postgresql/data
```

意思是「把一块持久存储挂到容器里的这个路径」。容器删了，数据还在。

两种卷：

| 写法 | 类型 | 用途 |
|---|---|---|
| `pgdata:/path` | 命名卷 | Docker 管理，用于数据持久化 |
| `./src:/app/src` | 绑定挂载 | 直接挂宿主机目录，用于开发时热更新 |

**三、healthcheck 保证启动顺序**

`depends_on` 只保证「db 容器启动了」，不保证「数据库准备好接受连接了」。加 `healthcheck` + `condition: service_healthy`，才是真的等它就绪。

不加的话，你的 api 会在数据库还没起来时就尝试连接，然后崩溃。

### 可能卡在哪

**api 连不上数据库**

按顺序检查：

1. 连接字符串里的主机名是不是服务名（`db` 而不是 `localhost`）
2. 用户名密码是不是和 db 服务的环境变量一致
3. `docker compose logs db` 看数据库是不是真的起来了
4. healthcheck 配了吗

**改了代码没生效**

如果挂载了 `./src:/app/src`，代码改动会实时生效，但 uvicorn 需要 `--reload` 才会重启。在 compose 里给 api 加 `command` 覆盖：

```yaml
command: ["uv", "run", "uvicorn", "csvstats.api:app", "--host", "0.0.0.0", "--reload"]
```

**`docker compose down -v` 之后数据没了**

`-v` 就是删卷的意思。**这个命令要慎用**，日常用不带 `-v` 的 `down`。

**端口冲突**

本机的 Postgres 或者上一个容器还占着 5432。停掉它，或者改映射端口。

### 背后的逻辑

Compose 的核心思想是「**基础设施即代码**」：你的运行环境不是靠一份文档描述「先装这个再装那个」，而是写成一个文件，任何人 `docker compose up` 就得到完全一样的环境。

这个文件进 git，和代码一起版本化。**新人入职第一天就能跑起完整环境**，不用花两天配环境。

到 S4 部署时，云平台要的也是同一个东西——你的镜像和它需要的配置。本地和线上用同一份定义，这就是 12-Factor App 里说的「开发环境与生产环境等价」。

---

## 完成判据

**动手部分**

<checkbox done="false">`docker compose up` 一条命令同时起 API 和数据库</checkbox>
<checkbox done="false">浏览器能访问 `http://localhost:8000/docs` 并调通接口</checkbox>
<checkbox done="false">数据写进数据库，`docker compose down` 再 `up` 之后数据还在</checkbox>
<checkbox done="false">`docker compose down -v` 之后数据被清空（验证卷确实在起作用）</checkbox>
<checkbox done="false">写了 `.dockerignore`，`.env` 和 `.venv` 都在里面</checkbox>
<checkbox done="false">镜像体积在 500MB 以内（`docker images` 查看）</checkbox>

**关键验证**：改一行 Python 代码，重新 `docker build`，**观察构建日志里有多少层用了缓存**。如果每次都重装依赖，说明 COPY 顺序写错了。

**理解检查**（笔记里回答）

1. 容器和虚拟机的区别是什么？容器本质上是什么？
2. 为什么 Dockerfile 里要分两次 COPY？
3. 容器里 uvicorn 为什么必须 `--host 0.0.0.0`？
4. 容器之间怎么互相访问？为什么不能用 localhost？
5. 命名卷和绑定挂载分别用在什么场景？
