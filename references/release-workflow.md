# GitHub Skill Release 工作流程

仅在发布或准备发布 Codex skill 到 GitHub 时使用本参考。

## 1. 检查源 skill

复制文件前，先确认 skill 文件夹并读取面向公开使用的文件：

- `SKILL.md`
- `README.md`，如果存在且准备公开
- `LICENSE`，如果存在
- `agents/openai.yaml`，如果存在
- 实际属于可复用 skill 的 `references/`、`scripts/` 或 `assets/` 文件

不要包含生成交付物、任务归档、本地日志、缓存目录、凭据、私人笔记或相邻的无关 skill。

## 2. 检查并融合绑定 skill

最终确定发布树前，检查目标 skill 是否绑定或依赖其他 skill。本流程中，如果目标 skill 明确调用另一个 skill，尤其是使用“美元符号加 skill 名”的显式调用语法，就视为绑定关系。

运行：

```bash
python scripts/inspect_skill_dependencies.py path/to/source-skill
```

辅助脚本会把显式绑定和可能的普通文字依赖分开。显式调用一般按确认绑定处理；普通文字如“使用 PDF skill”通常只是可能依赖，需要人工判断。判断前应人工检查 `SKILL.md`、`README.md`、`agents/openai.yaml` 以及相关 references/scripts。

依赖分类：

- 确认绑定：显式 skill 调用，或等价的直接命名调用。优先处理。
- 必需运行流程依赖：没有该依赖，公开后的 skill 无法完整使用。
- 可选助手或建议：有帮助，但不是必要条件。
- 内置工具或运行时能力：属于工具需求，不是需要发布的 skill 依赖。
- 误报：引用示例、变更记录或解释性文字。

对于确认绑定和必需 skill 依赖，应在发布前把必要行为融合进发布树：

- 简短规则优先直接写入目标 skill 的 `SKILL.md` 或现有 reference。
- 较长的可复用说明可放入 `references/integrated-skills/`。
- 用户自有且必要的确定性脚本可复制进发布树，并更新引用。
- 更新 README，确保用户安装公开仓库后不需要作者本地私有 skill。
- 移除或改写对其他 skill 的显式调用，避免仍要求用户安装额外私有 skill。
- 融合后重新运行安全审计。

不要在未确认公开权限时逐字复制私有、系统、内置或第三方 skill 内容。若直接公开权限不清楚，应概括其操作要求，或询问用户是把它作为公开前置条件，还是获得许可后再内联。

## 3. 收集用户选择

创建或修改远程仓库前，必须用选项形式让用户选择，并为每个重要设置提供自定义选项。

至少覆盖：

- 可见范围：公开、私有、组织内部可见，或自定义。
- 许可证：MIT、Apache-2.0、GPL-3.0、BSD-2-Clause/BSD-3-Clause、MPL-2.0、使用已有本地 `LICENSE`、不添加许可证，或自定义。
- 仓库名：推荐默认名或自定义。
- 描述：推荐描述、留空或自定义。
- README：使用现有 README、生成 README、省略或自定义。发布 skill 仓库的 README 默认使用中文；如果用户选择其他语言或双语，记录该选择，并保证标题、示例、安装说明、使用说明和限制说明都符合已批准语言。
- `.gitignore`：使用准备好的文件、使用平台模板、省略或自定义。
- Issues：开启、关闭或自定义。
- Wiki：开启、关闭或自定义。
- 推送时机：现在创建并推送、只创建仓库、稍后推送或自定义。
- GitHub Release：现在发布、跳过、创建草稿、创建预发布版或自定义。
- Release 资产：不附加、附加源码归档、附加指定文件或自定义。

解释每个设置的作用和主要风险。对公开可见范围，应明确说明公开内容可能被复制或缓存。

GitHub Release 版本号使用 `vMAJOR.MINOR.PATCH`：

- `v`：表示这是版本标签。
- `MAJOR`：用于大的、破坏性的，或会显著改变主要能力的更新。
- `MINOR`：用于新增优化、能力或功能模块，且保持原有用法兼容。
- `PATCH`：用于修复或小幅更正，不新增功能模块。

例如 `v1.1.1` 表示版本标签 `v`，大版本 `1`，新增功能/优化版本 `1`，修复版本 `1`。

更新已发布 skill 时，成功推送后必须询问 Release 选择。不要因为改动小就静默跳过。选项应包含：

- 立即发布稳定版。
- 创建草稿 Release。
- 创建预发布版。
- 跳过本次 Release。
- 自定义。

## 4. 构建干净发布树

创建单独的发布目录，只复制已选择公开的文件。

推荐 skill 仓库结构：

```text
skill-name/
|-- .gitattributes
|-- .gitignore
|-- LICENSE
|-- README.md
|-- SKILL.md
|-- agents/
|-- references/
`-- scripts/
```

新建仓库时添加 `.gitattributes`，用于统一文本换行：

```text
* text=auto eol=lf
```

使用能阻止本地和生成文件进入仓库的 `.gitignore`，例如：

```text
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
.pytest_cache/
*.tmp
*.temp
*.bak
*.orig
*.log
.DS_Store
Thumbs.db
desktop.ini
```

对于学术论文翻译等文档工作流，除非明确要发布示例文件，否则应考虑忽略生成的 `.docx`、`.pdf` 和核验报告。

创建或更新 `README.md` 时，除非用户明确选择其他语言，否则保持中文。README 必须只描述发布树中真实存在的能力。对于 skill 仓库，通常应包含解决什么问题、主要功能、安装方法、使用方法、输入输出示例和真实限制。

## 5. 提交前审计

在精确发布树上运行审计辅助脚本：

```bash
python scripts/audit_release_tree.py path/to/release-tree
```

同时人工检查文件清单。确认审计覆盖：

- 密码、API key、GitHub token、OAuth token、私钥和 bearer token。
- 个人信息，例如私人电子邮件账户、个人联络方式、证件编号、居住信息或不希望公开的本地用户名。
- 本地绝对路径，例如 Windows 用户目录、盘符路径、macOS 用户路径或 Linux home 路径。
- 临时文件、编辑器交换文件、缓存、编译产物、测试报告和日志。
- 私人笔记、草稿、内部专用文字或用户未打算公开的内容。

如果发现是误报，记录为什么安全；如果是真实问题，提交前先从发布树中移除。

## 6. 准备 Git 和 GitHub CLI

检查 Git 与 GitHub CLI：

```bash
git --version
gh --version
gh auth status
```

如果没有安装 `gh`，识别操作系统并提出官方安装程序或系统包管理器方案。涉及安装软件、管理员权限、系统设置变更或安装新包管理器时，先征得用户确认。

如果用户希望配置 HTTPS Git 凭据，使用：

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
```

遇到浏览器登录、通行密钥、验证码或二次验证时暂停，让用户本人操作。不要在对话中索要秘密信息。

### PowerShell 设备授权备用流程

仅当 `gh auth login --web` 无法请求设备码，但 PowerShell 能访问 GitHub HTTPS 接口时使用。

1. 使用 GitHub CLI 的公开 OAuth client id，通过 PowerShell 请求设备码。
2. 为用户打开 GitHub 设备登录页。
3. 只显示短的一次性用户码。
4. 在本地轮询 OAuth access token 接口，直到授权完成或过期。
5. 将返回的 token 直接传给 `gh auth login --with-token`。
6. 运行 `gh auth setup-git --hostname github.com`。
7. 删除临时设备授权状态。

绝不打印 access token，也不要把它写入发布树。

## 7. 提交并发布

必要时在发布树中初始化仓库：

```bash
git init
git branch -M main
git add .
git commit -m "Initial release"
```

使用仓库级提交身份。若用户不希望公开私人电子邮件账户，优先使用 GitHub noreply 形式。

只有在用户批准设置后，才创建远程仓库并推送：

```bash
gh repo create OWNER/REPO --public --description "DESCRIPTION" --source . --remote origin --push
```

按用户批准的设置添加参数，例如 `--private`、`--internal`、`--disable-issues` 或 `--disable-wiki`。

如果本地已有经过审计的 `LICENSE`，不要再要求 GitHub 生成另一份许可证模板，以免冲突。

## 8. 更新已发布 skill

当仓库已经存在，且用户要求更新、迭代、修订或发布新版本时，使用本节。

先确认：

- 包含本地新改动的源 skill 目录。
- 现有 GitHub 仓库，例如 `OWNER/REPO`。
- 当前本地发布副本，或从 GitHub 新克隆的干净副本。
- 最新推送提交和最新 GitHub Release 标签。

检查现有仓库状态：

```bash
gh repo view OWNER/REPO --json nameWithOwner,visibility,url,defaultBranchRef,hasIssuesEnabled,hasWikiEnabled
gh release list --repo OWNER/REPO --limit 10
```

在干净工作树中准备更新：

1. 拉取或克隆当前仓库状态。
2. 只复制预期更新的 skill 文件到仓库工作树。
3. 重新运行绑定 skill 检查。若出现新的确认绑定，提交前先融合必要且可公开的内容。
4. 重新在将要推送的精确目录上运行安全审计。
5. 检查 `git status`、`git diff --stat` 和关键差异，确认没有无关变更。
6. 如果差异会改变仓库行为、公开元数据、许可证、可见范围假设或 Release 包装方式，推送前让用户确认更新摘要。
7. 用描述实际更新内容的提交信息提交并推送。

规划版本时，让用户选择更新类型：

- Major：大的、不兼容的，或主能力变化。
- Minor：新增优化、功能或工作流模块。
- Patch：修复或小幅更正，不新增功能模块。
- 自定义版本。

如果已知最新标签，可用 `scripts/suggest_next_version.py` 辅助建议下一个版本：

```bash
python scripts/suggest_next_version.py v1.1.1 minor
```

每次成功推送更新后，都必须询问是否发布 GitHub Release。选项应包含稳定版、草稿、预发布版、跳过和自定义。若用户选择发布，继续执行 Release 章节。

## 9. 发布 GitHub Release

只有在用户明确批准 Release 选项后，才发布 GitHub Release。至少询问：

- 标签/版本号，例如 `v1.0.0`。
- Release 标题，例如 `v1.0.0`。
- Release 说明来源：生成摘要、用户提供说明或自定义。
- 草稿状态：立即发布或保存为草稿。
- 预发布状态：稳定版或预发布版。
- 附件资产：不附加、只附加源码归档、附加指定发布文件或自定义。

首次发布推荐默认值：`v1.0.0`，标题 `v1.0.0`，简洁说明初次公开发布内容，稳定版、非草稿，除非仓库有用户需要下载的打包文件，否则不附加额外资产。

在已推送标签后，或创建标签的同时，用 GitHub CLI 创建 Release：

```bash
gh release create v1.0.0 --repo OWNER/REPO --title "v1.0.0" --notes "Initial public release."
```

常用参数：

- `--draft`：创建草稿 Release。
- `--prerelease`：标记为预发布版。
- `--target main`：让标签指向某个分支或提交。
- 选项后追加资产路径：上传指定附件。

创建后核验 Release：

```bash
gh release view v1.0.0 --repo OWNER/REPO --json tagName,name,isDraft,isPrerelease,url
```

不要上传未经安全审计的附件。如果资产是在审计后生成的，应先审计最终资产再创建 Release。

## 10. 推送后核验

发布后核验：

- 仓库 URL。
- 可见范围。
- 默认分支。
- Issues 与 Wiki 设置。
- 本地远程 URL 和当前提交。
- 远程文件清单。
- 如发布了 Release，核验标签、标题、URL、草稿/预发布状态和资产。
- 使用新克隆或 GitHub 文件清单做最终安全确认。

清理临时克隆和临时授权状态文件。向用户报告仓库 URL、所选设置、提交号、文件清单、审计结果和剩余风险。
