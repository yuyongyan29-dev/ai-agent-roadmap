# U0.4 · Python 工程化（8 小时）

**这个单元解决什么问题**

上个单元你写的是「脚本」——一个文件，自己能跑。这个单元把它变成「项目」——有结构、有依赖声明、别人拿去能跑、以后能维护。

**这一步的价值不在于代码变好看了**，而在于：三个月后你回来看还能看懂，换台电脑能装起来，别人能贡献。这是「写代码的人」和「做软件的人」的分界线。

**学完你能做到**：建标准 Python 项目，管理依赖和虚拟环境，写出带类型注解和数据校验的代码。

---

## 步骤 1 · 理解虚拟环境（先想清楚再动手）

### 这一步在做什么

解决一个你迟早会撞上的问题：**项目 A 需要某个库的 1.0 版，项目 B 需要 2.0 版，装哪个？**

### 问题长什么样

假设你没有虚拟环境，所有库都装在系统 Python 里：

```
系统 Python
└── requests 2.0    ← 项目A 和 项目B 共用
```

某天项目 B 需要升级到 requests 3.0，你升了。**项目 A 突然跑不了了**，因为 3.0 改了接口。

这在真实开发里几乎每周发生一次，行话叫「依赖地狱」。

### 解法

给每个项目一个独立的 Python 环境：

```
项目A/.venv/  └── requests 2.0
项目B/.venv/  └── requests 3.0
```

互不干扰。这就是**虚拟环境**（virtual environment）。

### 怎么做

```bash
cd ~/Desktop/AI-Agent-学习计划
mkdir -p s0-foundation && cd s0-foundation
uv init csvstats
cd csvstats
ls -a
```

你会看到 uv 生成了这些：

| 文件 | 作用 |
|---|---|
| `pyproject.toml` | **项目的身份证**。项目名、版本、需要哪些依赖 |
| `.python-version` | 这个项目用哪个 Python 版本 |
| `main.py` | 一个示例入口文件 |
| `README.md` | 项目说明 |

装一个依赖试试：

```bash
uv add httpx
```

再 `ls -a`，多了两样：

| 文件 | 作用 |
|---|---|
| `.venv/` | **虚拟环境本体**。装的库都在这里面 |
| `uv.lock` | **锁文件**，精确记录每个包的确切版本 |

运行代码：

```bash
uv run python main.py
```

**注意是 `uv run python` 而不是 `python3`。** `uv run` 会自动使用这个项目的虚拟环境。

### `pyproject.toml` vs `uv.lock` 的区别

这是个重要区分：

- **`pyproject.toml`** 记录「我想要什么」，比如 `httpx>=0.27`。这是你手写或者 `uv add` 帮你写的。
- **`uv.lock`** 记录「实际装了什么」，精确到 `httpx==0.28.1` 以及它的每一个依赖的每一个版本。这是 uv 自动生成的。

**为什么要两个文件？** 因为 `>=0.27` 在今天可能解析成 0.28，明年可能是 0.35。锁文件保证你和你的同事、你的服务器装的是**完全一样的东西**。

**两个都要提交进 git。**

### 可能卡在哪

**`.venv` 被提交进 git 了**

`.venv` 有几百 MB，绝对不能提交。检查 `.gitignore` 里有没有 `.venv/`（你的仓库里已经有了）。

**不用 uv 行不行**

行，Python 自带 `venv` 模块：

```bash
python3 -m venv .venv
source .venv/bin/activate      # 激活
pip install httpx
deactivate                     # 退出
```

但你会发现两个麻烦：**必须记得激活**（忘了就装到系统里去了），以及 pip 装东西慢。uv 把这些都解决了，而且是 2026 年新项目的主流选择。

**已经用 pip 装了一堆东西到系统 Python 里，会不会有问题**

现阶段不会。以后想清理的话，`pip3 list` 看装了什么，`pip3 uninstall 包名` 卸载。

### 背后的逻辑

**虚拟环境本质上是什么？**

`.venv/` 就是一个普通目录，里面有：

```
.venv/
├── bin/python        ← 指向真实 Python 的软链接
├── bin/pip
└── lib/python3.13/site-packages/    ← 装的库都在这
```

「激活」虚拟环境做的事，只是**把 `.venv/bin` 加到 PATH 最前面**。这样你敲 `python` 时，找到的是虚拟环境里那个，而它会去自己的 `site-packages` 找库。

看，又是 PATH。U0.1 里学的那个概念在这里又用上了。**这种「同一个机制反复出现」的感觉，就是你开始入门的标志。**

---

## 步骤 2 · 把脚本重构成包

### 这一步在做什么

把 U0.3 的单文件 `csv_stats.py` 拆成有结构的模块。

### 为什么要拆

一个文件写到 300 行以上就没法维护了。拆分的原则是**按职责**：读数据的归读数据，算统计的归算统计，命令行界面归命令行界面。

好处很具体：改统计逻辑时不用看读文件的代码；写测试时可以单独测统计函数不用真的读文件。

### 怎么做

目标结构：

```
csvstats/
├── pyproject.toml
├── uv.lock
├── README.md
├── src/
│   └── csvstats/
│       ├── __init__.py       # 标记这是一个包
│       ├── models.py         # 数据结构定义
│       ├── reader.py         # 读 CSV
│       ├── stats.py          # 统计计算
│       └── cli.py            # 命令行入口
└── tests/                    # U0.7 再填
```

```bash
mkdir -p src/csvstats tests
touch src/csvstats/{__init__.py,models.py,reader.py,stats.py,cli.py}
rm main.py
```

把 U0.3 的代码按职责搬进对应文件。

模块之间这样互相引用：

```python
# src/csvstats/cli.py
from csvstats.reader import 读数据
from csvstats.stats import 统计
```

在 `pyproject.toml` 里告诉 uv 代码在 `src/` 下（uv init 生成的模板通常已经配好，检查一下）：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/csvstats"]
```

### 可能卡在哪

**`ModuleNotFoundError: No module named 'csvstats'`**

最常见的问题。原因是 Python 不知道去 `src/` 下面找。

解法：把项目本身装成「可编辑模式」：

```bash
uv sync
```

uv 会自动把你的项目装进虚拟环境（软链接方式，改代码立刻生效）。之后 `uv run python -m csvstats.cli` 就能跑。

**`__init__.py` 是干嘛的，能不能不要**

它标记「这个目录是一个 Python 包」。现代 Python 里可以省略（叫命名空间包），但**建议保留**，因为它同时是「放包级别初始化代码」的地方，而且能避免一些工具的诡异行为。

内容可以是空的，也可以放对外暴露的接口：

```python
# src/csvstats/__init__.py
from csvstats.stats import 统计

__all__ = ["统计"]
```

**改成包之后怎么运行**

三种方式：

```bash
uv run python -m csvstats.cli          # 作为模块运行
uv run csvstats                        # 如果在 pyproject.toml 配了入口点
uv run python src/csvstats/cli.py      # 直接跑文件（不推荐，import 会出问题）
```

配置命令行入口点的方法，在 `pyproject.toml` 加：

```toml
[project.scripts]
csvstats = "csvstats.cli:main"
```

然后 `uv sync`，之后就能 `uv run csvstats` 了。

### 背后的逻辑

**为什么代码要放在 `src/` 里？**

这叫 src-layout，和把包直接放在项目根目录（flat-layout）相对。

区别在于：flat-layout 时，你在项目根目录跑测试，Python 会直接从当前目录找到你的包，**哪怕你根本没装它**。这会掩盖打包配置的问题——你本地跑得好好的，别人 `pip install` 之后发现少文件。

src-layout 强制你必须真的装了包才能 import，**测试的是「装好之后的样子」，和用户拿到的一致**。

---

## 步骤 3 · 类与数据类

### 这一步在做什么

学会把「相关的数据和操作」打包在一起。

### 什么时候需要类

**不是所有代码都需要类。** 判断标准很简单：

- 一堆数据总是一起出现 → 用类（或 dataclass）打包它们
- 一个函数需要记住上次调用的状态 → 用类
- 就是一段计算逻辑，输入输出清晰 → **用函数就够了，别硬套类**

新手常见错误是把类当命名空间用，把一堆无关函数塞进一个类里。

### 怎么做

**普通类**：

```python
class 统计器:
    def __init__(self, 数值列: str):     # 初始化，创建对象时自动调用
        self.数值列 = 数值列              # self 是「这个对象自己」
        self.已处理 = 0

    def 处理(self, 行: dict) -> None:
        self.已处理 += 1
        ...

s = 统计器("销量")
s.处理({"销量": 100})
print(s.已处理)      # 1
```

**dataclass**（纯数据用这个，省掉一堆样板代码）：

```python
from dataclasses import dataclass

@dataclass
class 分组结果:
    分类: str
    数量: int
    均值: float

r = 分组结果("家电", 10, 3.5)
print(r)             # 分组结果(分类='家电', 数量=10, 均值=3.5)
print(r.均值)        # 3.5
```

`@dataclass` 自动帮你生成 `__init__`、`__repr__`（打印时的样子）、`__eq__`（比较）。**不用 dataclass 的话，上面这三行要写十几行。**

### 可能卡在哪

**`self` 是什么，为什么每个方法都要写**

`self` 指「调用这个方法的那个对象」。你写 `s.处理(行)`，Python 实际执行的是 `统计器.处理(s, 行)`——**对象自己被作为第一个参数传进去了**。

这是 Python 显式的设计选择：别的语言（Java、JS）也有这个机制，但用隐藏的 `this`。Python 认为显式比隐式好。

**忘了写 `self.`**

```python
class A:
    def __init__(self):
        计数 = 0          # 这只是个局部变量，函数结束就没了

    def 加(self):
        self.计数 += 1     # AttributeError: 没有 计数 这个属性
```

**属性必须用 `self.` 前缀**，否则它只是方法内部的临时变量。

**`@dataclass` 里可变默认值报错**

```python
@dataclass
class A:
    项目: list = []       # ValueError: mutable default
```

dataclass 直接禁止了这个写法（还记得 U0.3 的可变默认参数陷阱吗）。正确写法：

```python
from dataclasses import field

@dataclass
class A:
    项目: list = field(default_factory=list)
```

### 背后的逻辑

**`@dataclass` 上面那个 `@` 是什么？**

叫**装饰器**。它是一个「接收函数或类，返回改造后的函数或类」的东西。

```python
@dataclass
class A: ...

# 完全等价于
class A: ...
A = dataclass(A)
```

你现在不需要会写装饰器，但要能认出它、知道它在改造下面那个东西。你后面会大量遇到：`@app.get("/")`（FastAPI 路由）、`@pytest.fixture`（测试）、`@property`。

---

## 步骤 4 · 类型注解

### 这一步在做什么

给代码标注「这个变量应该是什么类型」，让工具能提前发现错误。

### 为什么值得做

Python 不检查类型，所以这种代码能跑到一半才炸：

```python
def 算均值(数字):
    return sum(数字) / len(数字)

算均值("abc")        # 运行到这里才报错
```

加上注解之后：

```python
def 算均值(数字: list[float]) -> float:
    return sum(数字) / len(数字)

算均值("abc")        # 编辑器立刻标红，还没运行就发现了
```

**注解不影响运行**，Python 运行时完全忽略它们。它的价值在于：

1. **编辑器能给你准确的自动补全**——这个提升非常明显
2. 类型检查器能在你写的时候就发现错误
3. **注解是最好的文档**，比注释准确，因为它不会过期

### 怎么做

常见写法：

```python
from pathlib import Path

数量: int = 5
名字: str = "小王"
比例: float = 0.5
开关: bool = True

标签: list[str] = ["a", "b"]
计数: dict[str, int] = {"a": 1}
坐标: tuple[int, int] = (1, 2)

# 可能是 None
备注: str | None = None

# 函数
def 处理(路径: Path, 限制: int = 10) -> list[dict[str, str]]:
    ...

# 不返回值
def 打印(内容: str) -> None:
    print(内容)
```

装类型检查器并跑一遍：

```bash
uv add --dev ty
uv run ty check src/
```

（或者用更成熟的 `mypy`：`uv add --dev mypy && uv run mypy src/`）

把报的错一个个改干净。

### 可能卡在哪

**报一堆错，不知道从哪改起**

从最基础的开始：先给所有函数的参数和返回值加注解，再处理内部变量。类型检查器的错误是有依赖关系的，改了上游下游可能自动就好了。

**`Optional[str]` 和 `str | None` 有什么区别**

一样的意思。`str | None` 是新写法（Python 3.10+），更简洁，**新代码用这个**。老代码里会看到 `from typing import Optional`。

**第三方库没有类型信息**

有些库不带类型标注，检查器会报 `missing imports`。解法是装对应的 stub 包（比如 `types-requests`），或者在配置里忽略这个库。

### 背后的逻辑

**为什么 Python 要事后加类型？**

Python 1991 年设计时，动态类型被认为是优点——写得快、灵活。这在小脚本上确实是。

但当代码规模到几万行、几十个人协作时，「这个参数到底该传什么」变成了巨大的沟通成本。所以 2014 年 Python 3.5 引入了类型注解，作为**可选的**补充。

关键词是「可选」：**Python 依然是动态类型语言**，注解只是给工具看的提示。这个设计让你可以渐进式地加类型——先给核心模块加，其余以后再说。

---

## 步骤 5 · Pydantic：数据校验

### 这一步在做什么

**这是本单元最重要的一步，因为它是整个 S1、S2 的基础。**

类型注解只是「提示」，运行时不检查。Pydantic 让类型注解真正生效：**数据进来先校验，不合格直接拒绝。**

### 为什么这对 Agent 开发至关重要

你在 S1 会遇到这个场景：大模型返回一段 JSON，你要用它。但模型可能：

- 少一个字段
- 把数字写成字符串
- 自己发明一个枚举值
- 在 JSON 外面包一层 markdown 代码块

如果不校验，这些错误会一路传下去，最后在一个完全不相干的地方崩掉，你根本查不到源头。

**Pydantic 让错误在最早的地方暴露，并且告诉你具体哪个字段错了。**

### 怎么做

```bash
uv add pydantic
```

```python
from pydantic import BaseModel, Field, field_validator

class 笔记(BaseModel):
    标题: str
    点赞数: int = Field(ge=0)                      # ge = 大于等于 0
    标签: list[str] = []
    作者: str | None = None

    @field_validator("标题")
    @classmethod
    def 标题不能为空(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("标题不能是空白")
        return v.strip()
```

用起来：

```python
# 正常
n = 笔记(标题="测试", 点赞数=10)
print(n.标题)

# 自动类型转换
n = 笔记(标题="测试", 点赞数="10")     # 字符串 "10" 自动转成整数 10

# 校验失败
n = 笔记(标题="测试", 点赞数=-1)
# ValidationError: 点赞数
#   Input should be greater than or equal to 0

# 从 JSON 直接构造
n = 笔记.model_validate_json('{"标题":"a","点赞数":5}')

# 转回 JSON
print(n.model_dump_json())
```

### 可能卡在哪

**`ValidationError` 信息看不懂**

Pydantic 的错误信息其实很详细，格式是：

```
1 validation error for 笔记
点赞数
  Input should be greater than or equal to 0 [type=greater_than_equal, input_value=-1]
```

三行分别是：出错的模型、出错的字段、为什么错以及你传的是什么。**从第二行开始读。**

**用了 Pydantic v1 的写法**

网上大量教程还是 v1 的。v2 改了不少名字：

| v1 | v2 |
|---|---|
| `@validator` | `@field_validator` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `parse_obj()` | `model_validate()` |

**你用的是 v2**，看教程时注意版本。

**什么时候用 dataclass，什么时候用 Pydantic**

- **数据来自外部**（用户输入、API 响应、读文件、模型输出）→ Pydantic，因为需要校验
- **数据是程序内部造的**，你能保证正确 → dataclass，更轻量

### 背后的逻辑

Pydantic 做的事叫「**边界校验**」：在数据进入你的系统的那一刻检查它，一旦通过，内部代码就可以放心地假设数据是干净的。

这个思路叫「**Parse, don't validate**」——不要到处写 `if x is None`，而是在入口处把不合格的数据挡在外面，之后的代码就不用再防了。

你在 S1 做结构化输出、S2 定义工具参数、S0 下个单元写 FastAPI 时，用的都是同一个 Pydantic 模型。**它是整个技术栈的粘合剂。**

---

## 步骤 6 · 日志

### 这一步在做什么

把 `print` 换成正规的日志。

### 为什么 print 不够

| 需求 | print | logging |
|---|---|---|
| 区分重要程度 | 做不到 | DEBUG / INFO / WARNING / ERROR |
| 上线后关掉调试输出 | 要删代码 | 改一个配置 |
| 知道是哪个模块打的 | 做不到 | 自动记录 |
| 带时间戳 | 手写 | 自动 |
| 同时输出到文件和屏幕 | 做不到 | 配置一下就行 |

到 S3 你会需要把日志和 trace 关联起来，那时 print 就完全不够用了。

### 怎么做

```python
import logging

logger = logging.getLogger(__name__)     # __name__ 是当前模块名

def 读数据(路径):
    logger.info("开始读取 %s", 路径)
    try:
        ...
    except FileNotFoundError:
        logger.error("文件不存在：%s", 路径)
        raise
    logger.debug("读到 %d 行", len(结果))
```

在程序入口配置一次：

```python
# cli.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
```

### 四个级别怎么选

| 级别 | 什么时候用 |
|---|---|
| `DEBUG` | 调试细节。正常运行时不显示 |
| `INFO` | 正常的关键节点。「开始处理」「完成，共 100 条」 |
| `WARNING` | 不正常但能继续。「第 5 行格式错误，已跳过」 |
| `ERROR` | 出错了，这次操作失败 |

### 可能卡在哪

**配了 logging 但什么都不输出**

`basicConfig` 默认级别是 WARNING，`logger.info()` 不会显示。要显示 INFO 就要设 `level=logging.INFO`。

**`basicConfig` 调了多次不生效**

它只有第一次调用生效。**只在程序入口调一次**，库代码里绝对不要调。

**为什么用 `logger.info("读到 %d 行", n)` 而不是 f-string**

```python
logger.debug(f"读到 {n} 行")           # 不管显不显示，字符串都会被拼出来
logger.debug("读到 %d 行", n)          # 只有真的要输出时才拼
```

日志量大时这个差别很明显。**养成用 `%s` 占位符的习惯。**

### 背后的逻辑

`logging.getLogger(__name__)` 这个写法有讲究。`__name__` 在 `src/csvstats/reader.py` 里的值是 `"csvstats.reader"`。

logging 模块用点号构建层级树：`csvstats.reader` 是 `csvstats` 的子 logger。这意味着你可以**统一控制一整个包的日志级别**：

```python
logging.getLogger("csvstats").setLevel(logging.DEBUG)      # 整个包开 DEBUG
logging.getLogger("httpx").setLevel(logging.WARNING)       # 第三方库只看警告
```

第二行在你接大模型 API 时会很有用——不然 httpx 会把每个 HTTP 请求的细节都刷屏。

---

## 步骤 7 · 代码风格工具

### 这一步在做什么

让工具自动帮你保持代码整洁，不用靠自觉。

### 怎么做

```bash
uv add --dev ruff
uv run ruff check --fix src/       # 检查并自动修复问题
uv run ruff format src/            # 格式化
```

在 `pyproject.toml` 里配一下：

```toml
[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

这几个规则集的含义：

| 代码 | 检查什么 |
|---|---|
| `E` | 代码风格（行太长、空格不对） |
| `F` | 逻辑问题（未使用的变量、未定义的名字） |
| `I` | import 顺序 |
| `UP` | 提示可以用更新的语法写法 |
| `B` | 常见 bug 模式（**比如可变默认参数**） |

VS Code 里装了 Ruff 插件的话，保存时会自动格式化（你的 `.vscode/settings.json` 已经配好了）。

### 可能卡在哪

**格式化把我的代码改了**

这是它的工作。**不要跟格式化工具争论。** 统一风格的价值远大于个人偏好，而且省下了所有关于「空格该几个」的争论时间。

**报了一堆 E501 行太长**

`ruff format` 会自动处理大部分。剩下的通常是长字符串或长注释，手动断行。

### 背后的逻辑

代码风格工具分两类：

- **formatter**（格式化器）：改代码的样子，不改逻辑。`ruff format`
- **linter**（检查器）：找出可疑的写法。`ruff check`

Ruff 用 Rust 写的，一个工具同时干这两件事，比传统的 black + flake8 + isort 组合快几十倍，而且只装一个。这是 2026 年 Python 项目的主流选择。

---

## 完成判据

**动手部分**

<checkbox done="false">`s0-foundation/csvstats/` 是一个标准 Python 项目，有 `pyproject.toml` 和 `uv.lock`</checkbox>
<checkbox done="false">代码拆成至少 4 个模块，职责清晰</checkbox>
<checkbox done="false">**所有函数都有参数和返回值的类型注解**</checkbox>
<checkbox done="false">至少一个 Pydantic 模型，能在数据不合法时给出清晰错误</checkbox>
<checkbox done="false">所有 `print` 换成 `logging`</checkbox>
<checkbox done="false">`uv run ruff check src/` 零报错</checkbox>
<checkbox done="false">类型检查零报错</checkbox>

**关键验证**：删掉 `.venv` 目录，然后

```bash
rm -rf .venv
uv sync
uv run csvstats data.csv
```

**能直接跑通**，说明你的依赖声明是完整的。这一步验证的是「换台电脑还能不能跑」。

**理解检查**（笔记里回答）

1. 虚拟环境解决什么问题？它本质上是什么？
2. `pyproject.toml` 和 `uv.lock` 分别记录什么，为什么要两个文件？
3. 类型注解会影响程序运行吗？那它有什么用？
4. 什么数据该用 Pydantic，什么数据用 dataclass 就够？
5. `logger.info("x=%s", x)` 比 `logger.info(f"x={x}")` 好在哪？
