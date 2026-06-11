# Git 初步使用说明（针对本项目）

##  克隆仓库（首次）
```bash
git clone <仓库URL>
cd nlp_project
```

##  分支策略

- **main**：生产环境代码，受保护，只能通过 PR 合并
- **develop**：开发主分支（可选，小团队可直接用 feature 分支指向 main）
- **feature/xxx**：新功能分支（例如 `feature/text-classification`）
- **fix/xxx**：bug 修复分支

##  日常工作流程

###  创建功能分支

bash

```
git checkout -b feature/your-feature-name
```

###  编写代码后查看变更

bash

```
git status
git diff
```

###  添加并提交（必须写语义化 message）

bash

```
git add .
git commit -m "feat: 实现文本分类API"
```

###  推送到远程仓库

bash

```
git push origin feature/your-feature-name
```

###  合并到 main（使用 Pull Request / Merge Request）

- 不要直接在 main 上 commit
- 在 GitHub/GitLab 上创建 PR，经过 code review 后合并

##  常用命令速查表

| 操作                          | 命令                       |
| ----------------------------- | -------------------------- |
| 查看所有分支                  | `git branch -a`            |
| 切换分支                      | `git checkout branch-name` |
| 拉取远程最新代码              | `git pull origin main`     |
| 放弃本地未提交的修改          | `git checkout -- <file>`   |
| 撤销上一次 commit（保留修改） | `git reset --soft HEAD~1`  |

##  禁止操作

- ❌ 禁止向 main 直接 push
- ❌ 禁止提交 `.env`, `__pycache__/`, `*.pyc`, `*.log`, `*.db`（这些应加入 `.gitignore`）
- ❌ 禁止提交大文件（模型文件 > 50MB），应使用 Git LFS 或外部存储

##  .gitignore 模板（执行以下命令创建）

bash

```
cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.pyc
*.pyo
.env
venv/
.venv/

# IDE
.vscode/
.idea/

# 模型文件
*.pkl
*.h5
*.pt
*.bin
models/

# 日志和数据
*.log
data/raw/
data/processed/

# 临时文件
.DS_Store
*.tmp
GITIGNORE
