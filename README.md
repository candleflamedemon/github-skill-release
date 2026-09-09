# GitHub Skill Release

`github-skill-release` 是一个 Codex 技能，用于将本地 Codex skill 安全整理、审计、发布到 GitHub，并支持后续更新和 GitHub Release 发布。

它适用于用户希望开源、发布、更新、迭代或 release 一个 Codex skill 仓库的场景。它不是独立的 GitHub 客户端，也不会绕过用户对仓库权限、许可证和发布范围的选择。

## 解决什么问题

将本地 skill 开源时，风险往往不只是在 GitHub 上创建仓库。还需要避免把本机路径、临时文件、测试残留、私人笔记、token、缓存目录或其他不该公开的内容一起推送出去。

同时，一个 skill 可能显式依赖作者本地的另一个 skill。如果直接发布，其他用户安装后可能缺少必要说明，导致公开版本不可复用。

本技能提供一套发布流程：先制作干净发布副本，检查并处理绑定 skill，补齐中文 README 和仓库卫生文件，执行秘密/隐私/路径审计，再在用户确认设置后创建或更新 GitHub 仓库，并按用户选择发布 GitHub Release。

## 主要功能

- 为目标 skill 构建单独的干净发布树，只包含计划公开的文件。
- 检查显式绑定的其他 skill，并指导将必要且可公开的说明融合到当前 skill 中。
- 默认要求 skill 仓库 README 使用中文；用户明确选择时可改为其他语言或双语。
- 在同一轮中同时提供一键推荐方案与所有适用设置的逐项选择题，不能隐藏其中任一部分。
- 为每项设置说明作用、选项效果和主要风险，标明推荐默认项，并始终保留自定义选项。
- 用户明确选择的项目优先；用户授权继续但未回答的项目使用已展示的推荐默认值，用户完全未回复时仍会等待。
- 使用 `scripts/audit_release_tree.py` 检查秘密、隐私、本地绝对路径、临时文件、测试残留和其他不应公开内容。
- 使用 `scripts/inspect_skill_dependencies.py` 检查 skill 之间的显式绑定和可能依赖。
- 使用 `scripts/suggest_next_version.py` 根据 `vMAJOR.MINOR.PATCH` 规则建议下一个版本号。
- 支持首次开源发布，也支持更新已发布 skill。
- 每次更新推送后都会询问是否发布 GitHub Release。
- 使用 GitHub CLI 完成仓库创建、推送、Release 发布和发布后核验。

## 安装方法

将本目录作为 Codex 技能放入 Codex 的技能目录中，例如：

```text
$CODEX_HOME/skills/github-skill-release
```

当前技能目录应至少包含以下文件：

```text
github-skill-release/
├── SKILL.md
├── agents/openai.yaml
├── references/release-workflow.md
└── scripts/
    ├── audit_release_tree.py
    ├── inspect_skill_dependencies.py
    └── suggest_next_version.py
```

使用 GitHub 发布功能时，需要本机安装 Git 和 GitHub CLI，也就是 `gh`，并完成 GitHub 授权。涉及账号密码、验证码、二次验证或浏览器授权时，应由用户本人完成，不应把密码或 token 发到对话中。

## 使用方法

在 Codex 中提供要发布的 skill 路径，并调用该技能，例如：

```text
使用 github-skill-release 将本地某个 Codex skill 开源发布到 GitHub。
```

典型流程包括：

1. 读取目标 skill 的公开文件。
2. 创建干净发布副本。
3. 检查是否绑定其他 skill，并处理必要依赖。
4. 准备中文 README、许可证、`.gitattributes` 和 `.gitignore`。
5. 运行安全审计。
6. 同时展示一键推荐方案和完整逐项选择题，说明推荐理由与风险，并等待用户至少回复一次。
7. 使用 GitHub CLI 创建或更新仓库。
8. 发布后核验仓库、文件清单、Release 状态和安全结果。

## 输入输出示例

### 输入

```text
请使用 github-skill-release 将 path/to/my-skill 开源到我的 GitHub，并发布 v1.0.0。
```

设置提问会同时包含两种回答方式：

```text
R. 一键采用推荐方案（映射：1A 2A 3B ...）

1. 可见范围：A. 公开（推荐） / B. 私有 / C. 组织内部 / D. 自定义
2. 许可证：A. MIT（推荐） / B. Apache-2.0 / ... / H. 自定义
...

可回复 R，也可回复 1B 2A 3C；未回答项在用户授权继续后使用已展示的推荐默认值。
```

### 输出

```text
GitHub 仓库：
https://github.com/owner/my-skill

Release：
https://github.com/owner/my-skill/releases/tag/v1.0.0

发布文件：
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── SKILL.md
├── agents/openai.yaml
├── references/...
└── scripts/...
```

实际仓库名、可见范围、许可证、Release 版本号和是否附加资产都应以用户选择为准。

## 脚本说明

### `scripts/audit_release_tree.py`

检查发布树中是否存在可能不应公开的内容，包括秘密、token、个人信息、本地绝对路径、临时文件、缓存、测试残留和内部专用内容。

示例：

```bash
python scripts/audit_release_tree.py path/to/release-tree
```

### `scripts/inspect_skill_dependencies.py`

检查 skill 文本中是否存在显式调用其他 skill 的语法，并列出可能的普通文字依赖，供发布前人工判断。

示例：

```bash
python scripts/inspect_skill_dependencies.py path/to/source-skill
```

### `scripts/suggest_next_version.py`

根据当前版本号和更新类型建议下一个 Release 标签。

示例：

```bash
python scripts/suggest_next_version.py v1.1.1 minor
```

输出：

```text
v1.2.0
```

## 真实能力边界

- 本技能提供的是 Codex 执行安全开源发布时应遵循的流程和辅助脚本。
- 它会同时展示推荐方案和逐项选项，不会在展示前替用户决定设置。用户授权继续但省略部分项目时，会使用事先明确标出的推荐默认值；完全没有用户回复时不会执行远程操作。
- 它不能保证 GitHub、GitHub CLI、网络或账号授权始终可用；遇到授权步骤时需要用户本人完成。
- 审计脚本是辅助工具，不能替代对发布文件清单和内容的人工确认。

---

# GitHub Skill Release

`github-skill-release` is a Codex skill for safely preparing, auditing, publishing, updating, and releasing local Codex skills on GitHub.

It applies when a user wants to open-source, publish, update, iterate on, or create a GitHub Release for a Codex skill repository. It is not a standalone GitHub client and does not bypass the user's choices about repository permissions, license, or release scope.

## Problem Solved

Publishing a local skill is not only about creating a GitHub repository. The release process also needs to avoid exposing local paths, temporary files, test leftovers, private notes, tokens, cache folders, or other content that should not become public.

A skill can also explicitly depend on another local skill owned by the author. If it is published as-is, other users may not have the required instructions and the public version may not be reusable.

This skill provides a release workflow: build a clean release copy, inspect and handle bound skills, prepare a README and repository hygiene files, audit for secrets/privacy/paths, create or update the GitHub repository only after user-approved settings, and publish a GitHub Release when approved.

## Main Features

- Build a clean release tree for the target skill with only intended public files.
- Inspect explicit bindings to other skills and guide integration of necessary publishable instructions into the current skill.
- Default published skill READMEs to Chinese; use another language or bilingual README only when the user chooses it.
- Present a one-click recommended bundle and all applicable per-setting multiple-choice questions together; neither part is hidden behind the other.
- Explain each setting, option effect, and primary risk, mark the recommended default, and always include a custom option.
- Honor explicit choices first; after the user authorizes continuation, fill unanswered settings from the displayed defaults, while still waiting if the user has not replied at all.
- Use `scripts/audit_release_tree.py` to check for secrets, privacy issues, local absolute paths, temporary files, test leftovers, and other non-public content.
- Use `scripts/inspect_skill_dependencies.py` to detect explicit skill bindings and possible prose dependencies.
- Use `scripts/suggest_next_version.py` to suggest the next version tag according to `vMAJOR.MINOR.PATCH`.
- Support both initial open-source publishing and updates to already published skills.
- Ask whether to publish a GitHub Release after every completed update push.
- Use GitHub CLI for repository creation, pushing, Release publishing, and post-publish verification.

## Installation

Place this directory in the Codex skills folder, for example:

```text
$CODEX_HOME/skills/github-skill-release
```

The skill directory should contain at least:

```text
github-skill-release/
├── SKILL.md
├── agents/openai.yaml
├── references/release-workflow.md
└── scripts/
    ├── audit_release_tree.py
    ├── inspect_skill_dependencies.py
    └── suggest_next_version.py
```

GitHub publishing requires Git and GitHub CLI (`gh`) to be installed and authenticated. If account credentials, verification codes, two-factor authentication, or browser authorization are required, the user should complete those steps directly and should not send passwords or tokens in chat.

## Usage

Provide the path to the skill that should be published and invoke this skill in Codex, for example:

```text
Invoke github-skill-release for a local Codex package that should be open-sourced on my GitHub.
```

A typical workflow includes:

1. Review the public files from the target package.
2. Create a clean release copy.
3. Check whether the package is bound to other skills and handle required dependencies.
4. Prepare README, license, `.gitattributes`, and `.gitignore`.
5. Run the safety audit.
6. Present the recommended bundle and the complete per-setting questions together, explain the rationale and risks, and wait for at least one user reply.
7. Use GitHub CLI to create or update the repository.
8. Verify the repository, file list, Release status, and safety result after publishing.

## Input and Output Example

### Input

```text
Please use github-skill-release to open-source path/to/my-skill on my GitHub and publish v1.0.0.
```

The settings prompt supports both response styles at the same time:

```text
R. Apply the recommended bundle (mapping: 1A 2A 3B ...)

1. Visibility: A. Public (recommended) / B. Private / C. Internal / D. Custom
2. License: A. MIT (recommended) / B. Apache-2.0 / ... / H. Custom
...

Reply with R or selections such as 1B 2A 3C. After authorization, unanswered items use the displayed recommended defaults.
```

### Output

```text
GitHub repository:
https://github.com/owner/my-skill

Release:
https://github.com/owner/my-skill/releases/tag/v1.0.0

Published files:
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── SKILL.md
├── agents/openai.yaml
├── references/...
└── scripts/...
```

The actual repository name, visibility, license, Release version, and attached assets must follow the user's approved choices.

## Scripts

### `scripts/audit_release_tree.py`

Checks the release tree for content that may be unsafe to publish, including secrets, tokens, personal information, local absolute paths, temporary files, caches, test leftovers, and internal-only content.

Example:

```bash
python scripts/audit_release_tree.py path/to/release-tree
```

### `scripts/inspect_skill_dependencies.py`

Checks skill text for explicit invocations of other skills and lists possible prose dependencies for manual review before publishing.

Example:

```bash
python scripts/inspect_skill_dependencies.py path/to/source-skill
```

### `scripts/suggest_next_version.py`

Suggests the next Release tag from the current version and update type.

Example:

```bash
python scripts/suggest_next_version.py v1.1.1 minor
```

Output:

```text
v1.2.0
```

## Real Limitations

- This skill provides a workflow and helper scripts for safe open-source publishing in Codex.
- It presents both recommendations and per-setting choices before acting. After the user authorizes continuation, omitted items use the explicitly displayed defaults; no remote operation runs without any user reply.
- It cannot guarantee that GitHub, GitHub CLI, network access, or account authorization will always be available.
- The audit script is a helper and does not replace manual review of the public file list and file contents.
