# U0.2 · Git 与 GitHub（6 小时）

**这个单元解决什么问题**

你写代码会改错。改错之后想回到昨天那版，靠「另存为 副本2 最终版 真的最终版」是不行的。Git 解决的就是这件事：**它记录你代码的每一次改动，让你能随时回到任何一个历史时刻。**

顺便，它还解决另外两件事：把代码备份到云端（GitHub），以及多个人改同一份代码时怎么合并。

**学完你能做到**：改代码不再害怕；出错能回退；代码有云端备份；能看懂 GitHub 上的项目历史。

---

## 先建立一个心智模型

在敲任何命令之前，先理解 Git 的三个「区域」。**这是整个单元最重要的一段，看不懂就往下读，做完练习再回来看。**

想象你在写一篇论文，要交给导师存档。

| 区域 | 类比 | Git 里叫什么 |
|---|---|---|
| 你正在改的文件 | 桌上摊开的草稿 | **工作区**（Working Directory） |
| 你挑出来准备交的几页 | 放进文件夹的那几页 | **暂存区**（Staging Area / Index） |
| 导师收下并归档的版本 | 档案柜里的一份存档 | **仓库**（Repository） |

对应三条命令：

```
工作区  --git add-->  暂存区  --git commit-->  仓库
```

**为什么要有中间那个暂存区？** 因为你可能同时改了 5 个文件，但其中 3 个是修 bug、2 个是加新功能。你希望它们分成两次存档，而不是混成一坨。暂存区让你能挑选「这次要存哪几个改动」。

新手最容易懵的就是这里。**接下来每敲一条命令，你都要跑一次 `git status` 看文件在哪个区域。** 敲十几次之后这个模型就刻进脑子了。

---

## 步骤 1 · 配置你的身份

### 这一步在做什么

告诉 Git「我是谁」。每一次存档都会记下作者名字和邮箱，这样以后看历史能知道哪行是谁写的。

### 怎么做

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

验证：

```bash
git config --global --list
```

顺便设两个有用的默认值：

```bash
git config --global init.defaultBranch main    # 新仓库的主分支叫 main
git config --global pull.rebase false          # pull 时用 merge 策略
```

### 可能卡在哪

**邮箱要用真实的吗**

如果你要用 GitHub，**建议用你注册 GitHub 的那个邮箱**，这样 GitHub 才能把提交关联到你的账号（贡献图上才有格子）。不想暴露真实邮箱的话，GitHub 提供一个 `xxx@users.noreply.github.com` 形式的隐私邮箱，在 GitHub 设置里能找到。

**`--global` 是什么意思**

表示「对这台电脑上所有仓库生效」。如果某个项目要用不同身份（比如公司项目用公司邮箱），在那个项目目录里跑不带 `--global` 的同样命令，就只对它生效。

### 背后的逻辑

Git 的配置有三层，优先级从低到高：

1. 系统级（`/etc/gitconfig`）——很少用
2. 全局级（`~/.gitconfig`）——就是 `--global`，你的个人默认
3. 仓库级（项目里的 `.git/config`）——覆盖上面两层

这种「层层覆盖」的配置模式在开发工具里极其常见，你后面会在 VS Code、Docker、Python 项目里反复见到同样的设计。

---

## 步骤 2 · 走一遍完整流程

### 这一步在做什么

亲手把一个改动从工作区送到仓库，并且每一步都看清楚它在哪。

### 怎么做

在你的学习仓库里做（就是桌面那个文件夹）：

```bash
cd ~/Desktop/AI-Agent-学习计划
```

**第一次：看看现在什么样**

```bash
git status
```

大概率显示 `nothing to commit, working tree clean`——意思是「工作区干净，没有未保存的改动」。

**第二次：制造一个改动**

```bash
echo "# 我的学习笔记" > 测试.md
git status
```

现在会看到：

```
Untracked files:
  测试.md
```

**`Untracked` 的意思是「Git 还不认识这个文件」**。它在你的工作区，但 Git 从没管过它。

**第三次：放进暂存区**

```bash
git add 测试.md
git status
```

现在变成：

```
Changes to be committed:
  new file: 测试.md
```

**`Changes to be committed` 就是暂存区。** 文件从「Git 不认识」变成了「Git 准备存档它」。

**第四次：存档**

```bash
git commit -m "添加测试笔记"
git status
```

回到 `working tree clean`。改动已经归档了。

**第五次：改一下已有文件，再看**

```bash
echo "第二行" >> 测试.md
git status
```

这次显示：

```
Changes not staged for commit:
  modified: 测试.md
```

**注意这次不是 `Untracked` 而是 `modified`**——因为 Git 已经认识这个文件了，它知道你改了什么。

`git add` + `git commit` 再走一遍。

### 看看你都存了什么

```bash
git log --oneline
```

每行一个存档点，前面那串字符是「提交哈希」，是这次存档的唯一编号。

```bash
git log            # 完整信息：作者、时间、完整哈希
git show           # 看最近一次提交具体改了什么
git diff           # 看工作区还有什么改动没 add
git diff --staged  # 看暂存区里有什么改动没 commit
```

### 可能卡在哪

**`git commit` 之后跳进一个奇怪的全屏编辑器，退不出来**

你忘了加 `-m "提交信息"`，Git 就打开编辑器让你写。这个编辑器多半是 vim。

**逃出来的方法**：按 `Esc`，然后输入 `:wq` 回车（保存退出），或者 `:q!` 回车（不保存退出）。

以后记得永远带 `-m`。

**`nothing added to commit but untracked files present`**

你直接 commit 了，但没 add。文件还在工作区，没进暂存区。先 `git add`。

**`git add .` 和 `git add 文件名` 有什么区别**

`.` 表示「当前目录下所有改动」。图省事可以用，但**养成先 `git status` 看一眼再 add 的习惯**，避免误提交不该提交的东西（比如密钥文件）。

### 背后的逻辑

**提交哈希是什么？**

那串 40 位的十六进制字符（`git log --oneline` 只显示前 7 位）是这次提交所有内容算出来的 SHA-1 哈希值。它包括：这次的文件快照、作者、时间、提交信息、以及**上一次提交的哈希**。

「包含上一次提交的哈希」这一点很关键。它意味着每个提交都指向它的父提交，串成一条链。你改动历史里任何一个提交，它后面所有提交的哈希都会变。**这就是为什么 Git 的历史是不可篡改的**——这也是区块链的同一个原理。

**Git 存的是快照还是差异？**

常见误解是 Git 存「每次改了哪几行」。实际上 **Git 存的是每次提交时整个项目的完整快照**（没变的文件用指针指向旧版本，所以不浪费空间）。`git diff` 显示的差异是它临时算出来给你看的。

这个设计让「切换到任意历史版本」变得极快——直接取那个快照就行，不用一层层回放差异。

---

## 步骤 3 · 写 .gitignore

### 这一步在做什么

告诉 Git「这些文件永远不要管」。

### 为什么必须做

有三类文件绝对不能进 Git：

| 类型 | 例子 | 为什么 |
|---|---|---|
| **密钥** | `.env`、`config.json` 里的 API key | **提交上去就等于公开了**。GitHub 上有机器人专门扫这个，几分钟内你的密钥就会被盗刷 |
| **依赖包** | `node_modules/`、`.venv/` | 几万个文件几百 MB，而且能靠配置文件重新下载，存进去纯属浪费 |
| **生成物** | `__pycache__/`、`dist/`、`.DS_Store` | 编译或运行产生的，随时能重新生成 |

### 怎么做

你的仓库里已经有 `.gitignore` 了，看看：

```bash
cat .gitignore
```

自己加一条试试：

```bash
echo "测试.md" >> .gitignore
git status
```

`测试.md` 从列表里消失了——Git 现在无视它。

（练习完记得把这行删掉，或者把 `测试.md` 删了。）

### 可能卡在哪

**加进 .gitignore 了但文件还在 Git 里**

**这是最经典的坑。** `.gitignore` 只对「Git 还不认识的文件」生效。如果一个文件已经被 `git add` 过了，Git 就一直跟踪它，加进 ignore 也没用。

解法是让 Git 忘掉它：

```bash
git rm --cached 文件名        # 从 Git 移除，但保留本地文件
git commit -m "停止跟踪 xxx"
```

注意 `--cached` 千万别漏，漏了会连本地文件一起删。

**密钥已经提交并推到 GitHub 了怎么办**

**立刻去服务商后台把那个密钥作废重新生成。** 不要指望删掉提交就没事了——Git 的历史里还有，别人可能已经克隆走了。

删历史记录是次要的，作废密钥才是第一优先级。

### 背后的逻辑

`.gitignore` 的匹配规则：

| 写法 | 匹配什么 |
|---|---|
| `*.log` | 所有 .log 文件 |
| `build/` | 名为 build 的目录（末尾斜杠表示只匹配目录） |
| `/config.json` | 只匹配根目录下的这个文件（开头斜杠锚定根） |
| `!important.log` | 排除中的例外（感叹号取反） |

GitHub 维护了一份[各语言的标准 .gitignore 模板](https://github.com/github/gitignore)，新项目直接抄对应语言那份就行。

---

## 步骤 4 · 撤销：三种「我改错了」

### 这一步在做什么

学会救命的命令。**新手最怕的不是写错代码，是不知道怎么退回去。**

### 三种情况，三个命令

**情况一：改了工作区，还没 add，想丢弃**

```bash
echo "写错了" >> 测试.md
git status                    # 显示 modified
git restore 测试.md            # 丢弃改动，恢复到上次提交的样子
git status                    # 干净了
```

**情况二：已经 add 了，想退回工作区（不丢改动）**

```bash
echo "又改了" >> 测试.md
git add 测试.md
git status                    # 在暂存区
git restore --staged 测试.md   # 退出暂存区，改动还在工作区
git status                    # 变回 modified
```

**情况三：已经 commit 了，想撤销这次提交**

```bash
git revert HEAD
```

这会**新建一次提交**，内容是把上次提交的改动反着做一遍。

### 为什么撤销提交要「反着做一遍」而不是删掉

因为删除历史是危险的。如果这个提交已经推给别人了，你删掉它，别人的仓库就和你对不上了。

`git revert` 的做法是「用一次新提交抵消旧提交」，历史链条完整，谁看都清楚发生了什么。**这是团队协作里唯一安全的撤销方式。**

（确实有删除历史的命令 `git reset --hard`，但它只应该用在「还没推给任何人」的本地提交上。现阶段先别碰。）

### 可能卡在哪

**`git restore` 之后改动真的没了**

对，这个操作不可逆。**所以养成小步提交的习惯**——改一点点就 commit 一次。提交是免费的，后悔是昂贵的。

**HEAD 是什么**

`HEAD` 是一个指针，指向「你当前所在的位置」，通常就是最新的那次提交。

- `HEAD` = 最新提交
- `HEAD~1` = 上一次
- `HEAD~3` = 往前数三次

### 背后的逻辑

Git 的命令名字历史上很混乱（`checkout` 一个命令干五件事），所以 Git 2.23 之后拆出了两个语义清晰的新命令：

- `git switch` —— 只管切换分支
- `git restore` —— 只管恢复文件

你在网上会看到大量老教程用 `git checkout`。它还能用，但**新代码建议用新命令**，语义清楚不容易搞错。

---

## 步骤 5 · 分支：并行地改

### 这一步在做什么

学会「开一条支线做实验，不影响主线」。

### 怎么做

```bash
git switch -c 试验              # 新建分支「试验」并切过去（-c 是 create）
git branch                     # 看所有分支，* 号标记当前在哪

echo "试验内容" > 试验.md
git add 试验.md
git commit -m "试验：加了个文件"

git switch main                # 切回主分支
ls                             # 试验.md 不见了！

git switch 试验                 # 切回去
ls                             # 又出现了
```

**文件「消失」不是删除，是 Git 把工作区切换成了那个分支的样子。**

### 合并回主线

```bash
git switch main
git merge 试验
ls                             # 现在 main 上也有试验.md 了
git branch -d 试验              # 删掉已合并的分支（-d 是 delete）
```

### 制造并解决一次冲突

**这一步必须亲手做一次**，否则第一次在真实项目里遇到会慌。

```bash
# 在 main 上改某一行
echo "main 的版本" > 冲突.md
git add . && git commit -m "main 改了冲突.md"

# 开个分支，改同一行
git switch -c 分支A
echo "分支A 的版本" > 冲突.md
git add . && git commit -m "分支A 改了冲突.md"

# 回主线合并
git switch main
git merge 分支A
```

会报：

```
CONFLICT (content): Merge conflict in 冲突.md
Automatic merge failed; fix conflicts and then commit the result.
```

打开 `冲突.md`（在 VS Code 里打开更清楚），会看到：

```
<<<<<<< HEAD
main 的版本
=======
分支A 的版本
>>>>>>> 分支A
```

**这三行标记的含义**：

| 标记 | 含义 |
|---|---|
| `<<<<<<< HEAD` | 从这里开始是**当前分支**（main）的版本 |
| `=======` | 分界线 |
| `>>>>>>> 分支A` | 到这里结束是**被合并分支**的版本 |

**你要做的是**：手动编辑成你想要的最终内容，**把三行标记全部删掉**，然后：

```bash
git add 冲突.md
git commit -m "解决冲突"
```

在 VS Code 里，冲突处会有 `采用当前更改 / 采用传入的更改 / 保留双方更改` 的按钮，点一下就行，比手改快。

### 可能卡在哪

**合并到一半反悔了**

```bash
git merge --abort
```

回到合并前的状态。

**解决完冲突忘了删标记**

代码里留着 `<<<<<<<` 会导致程序语法错误。提交前搜一下：

```bash
grep -rn "<<<<<<<" .
```

**`git switch` 报 `Your local changes would be overwritten`**

你当前有未提交的改动，切分支会冲掉它们。两个选择：先 commit，或者用 `git stash` 把改动临时收起来（`git stash pop` 取回来）。

### 背后的逻辑

**分支到底是什么？**

这是 Git 最反直觉也最优雅的地方：**分支只是一个指向某次提交的指针，就是一个存了 40 字符哈希值的小文件。**

你可以自己看：

```bash
cat .git/refs/heads/main
```

输出就是一串哈希。

所以在 Git 里新建分支的成本几乎是零——不复制任何文件，只是写一个 41 字节的文件。这就是为什么 Git 鼓励你随便开分支，而老一代版本控制工具（比如 SVN）里开分支是要复制整个目录的重活。

**`git switch` 切分支时发生了什么？**

Git 把 HEAD 指针指向新分支，然后把工作区的文件替换成那个分支所指向的提交的快照。所以文件才会「消失」和「出现」。

---

## 步骤 6 · 推到 GitHub

### 这一步在做什么

把本地仓库同步到云端，既是备份，也是给别人看的窗口。

### 怎么做

你的仓库已经连好 GitHub 了，验证一下：

```bash
git remote -v
```

会显示 `origin  https://github.com/你的用户名/ai-agent-roadmap.git`。

**`origin` 是这个远程仓库的代号**，是约定俗成的默认名字，不是关键字。

日常三件套：

```bash
git status              # 看有什么改动
git add -A              # 全部加入暂存区（-A 是 all）
git commit -m "说明"
git push                # 推到 GitHub
```

拉取别人（或你在另一台电脑上）的改动：

```bash
git pull
```

### 提交信息怎么写

**这是会影响你面试的细节。** 招聘方看你的 GitHub，提交历史一眼就能看出工程素养。

坏例子：`update`、`fix`、`1`、`aaa`、`修改`

好例子：

```
U0.2: 完成 Git 基础练习
fix: 修复 CSV 解析在空行时崩溃
docs: 补充 RAG 检索的对比数据
```

推荐用「类型: 做了什么」的格式。常见类型：`feat`（新功能）、`fix`（修 bug）、`docs`（文档）、`test`（测试）、`refactor`（重构）、`chore`（杂务）。

### 可能卡在哪

**`git push` 要求输入用户名密码，输了还是失败**

GitHub 在 2021 年就取消了密码认证。你已经装了 `gh`，用它登录一次就行：

```bash
gh auth login
```

按提示选 GitHub.com → HTTPS → 用浏览器登录。登录后 git 会自动使用它的凭证。

**`rejected` / `non-fast-forward`**

远程有你本地没有的提交（比如你在网页上改过文件）。先拉再推：

```bash
git pull
git push
```

如果 pull 时有冲突，按步骤 5 的方法解决。

**推上去发现有不该推的文件**

见步骤 3 的 `git rm --cached`。如果是密钥，**第一件事是去作废密钥**。

### 背后的逻辑

Git 是**分布式**版本控制。这意味着你电脑上的仓库是完整的——包含全部历史，不依赖网络。GitHub 只是「另一个仓库」，恰好放在云上，大家约定用它同步。

这跟 SVN 那种「中央服务器」模式根本不同。断网时你照样能提交、切分支、看历史，只是不能 push/pull。

`origin/main` 这个写法你会经常看到，它表示「origin 这个远程仓库上的 main 分支，在我上次同步时的样子」。它和你本地的 `main` 是两个独立的指针，`git pull` 就是去更新前者并合并到后者。

---

## 完成判据

**动手部分**

<checkbox done="false">你的学习仓库有 5 个以上语义清晰的 commit</checkbox>
<checkbox done="false">完整走过一次：建分支 → 改动 → 提交 → 合并 → 删分支</checkbox>
<checkbox done="false">**亲手制造并解决过一次 merge 冲突**</checkbox>
<checkbox done="false">用过 `git restore` 丢弃改动、`git restore --staged` 退出暂存区</checkbox>
<checkbox done="false">成功 push 到 GitHub</checkbox>

**理解部分**（在单元笔记里回答，不看资料）

1. `git add` 和 `git commit` 分别把文件从哪里移到哪里？
2. 我改错了但还没提交，用什么命令？我改错了已经提交了，用什么命令？
3. 分支的本质是什么？为什么在 Git 里开分支很便宜？
4. 为什么 `.gitignore` 对已经提交过的文件不起作用？

**推荐加练**：[Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN)，中文交互式，主线一小时能过完。它用动画把分支和合并画出来，比看文字直观十倍。

---

## 一张速查表

存下来，前两周会天天看。

```bash
# 日常
git status                    # 我现在什么情况（不确定时先敲这个）
git add -A                    # 全部进暂存区
git commit -m "说明"           # 存档
git push                      # 推到云端
git pull                      # 拉取云端

# 看
git log --oneline             # 简洁历史
git diff                      # 工作区有什么没 add 的改动
git diff --staged             # 暂存区有什么没 commit 的改动
git show                      # 最近一次提交改了什么

# 撤销
git restore 文件               # 丢弃工作区改动
git restore --staged 文件      # 退出暂存区
git revert HEAD               # 撤销最近一次提交（新建反向提交）
git merge --abort             # 放弃正在进行的合并

# 分支
git switch -c 名字             # 新建并切换
git switch main               # 切换
git branch                    # 列出
git merge 分支名               # 合并进当前分支
git branch -d 分支名           # 删除
git stash                     # 临时收起改动
git stash pop                 # 取回
```
