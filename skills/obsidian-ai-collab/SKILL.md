---
name: obsidian-ai-collab
description: "Use this skill whenever the user wants to design, improve, or operate an Obsidian vault as an AI-collaboration system: folder structure, Inbox/Journal/Garden/Projects/Areas organization, MOCs (Maps of Content), evergreen notes, promoting journal notes into permanent notes, or prompting Claude Code/AI to work inside an Obsidian vault. Also use it when the user shares note-taking workflows inspired by Zettelkasten, linked thinking, or asks how to make AI useful with real note context."
---

# Obsidian AI Collaboration

Turn a plain Obsidian vault into a lightweight system where the human thinks and the AI helps with context, synthesis, drafting, and project momentum.

## What this skill is for

Use this skill when the user wants any of the following:
- Create a practical Obsidian folder structure
- Separate fleeting notes, journals, evergreen notes, projects, and long-term areas
- Build or refine MOCs (Maps of Content)
- Turn messy notes into reusable knowledge
- Decide how Claude Code or other coding/terminal agents should work inside a vault
- Create prompts/workflows for note review, link discovery, synthesis, and project planning

This skill is intentionally biased toward **simple systems that survive real usage**. Prefer lightweight structure over elaborate taxonomies.

## Core model

Recommend this default structure unless the user already has a better one:

```text
01 Inbox/
02 Journal/
03 Garden/
04 Projects/
05 Areas/
99 MOCs/
```

### Folder roles
- **01 Inbox**: quick capture, fragments, unprocessed notes
- **02 Journal**: daily thinking, reflections, planning, rough notes
- **03 Garden**: permanent notes worth keeping; atomic, opinionated, linked
- **04 Projects**: active work with clear deliverables and next steps
- **05 Areas**: ongoing responsibilities or life domains
- **99 MOCs**: entry points that organize clusters of notes by theme

## Operating principles

### 1. Keep the vault legible
Prefer a small number of obvious folders over clever systems. If the user sounds attracted to heavy tagging, complex metadata, or elaborate templates, point out the maintenance cost.

### 2. Distinguish raw thinking from durable thinking
Journal notes are for processing. Garden notes are for retention. Do not blur them unless the user explicitly wants a more fluid system.

### 3. Make notes worth linking
Garden notes should usually be:
- **Atomic**: one idea per note
- **Opinionated**: make a claim, not just name a topic
- **Linked**: connect to nearby ideas, tensions, examples, and projects

### 4. Give AI scoped context
When helping the user use AI in Obsidian, advise them to point the AI at the right MOC, folder, or project directory instead of the whole vault whenever possible.

### 5. AI should think with the user, not replace them
Frame AI as useful for:
- finding gaps
- surfacing hidden connections
- challenging assumptions
- clustering themes
- drafting from the user's own material

Do not frame AI as the author of truth. The human remains the editor and decision-maker.

## Default templates

### Evergreen / Garden note
Use when the user asks for an atomic note format:

```markdown
# 观点：<一句话结论>

## 核心论点
- 

## 依据/例子
- 

## 反例/边界
- 

## 关联
- [[相关笔记A]]
- [[相关笔记B]]

#tags
```

Why this works: it forces the note to carry a real idea, some support, some boundary, and some links.

### Project note
Use inside `04 Projects/<project>/README.md` unless the user prefers another convention:

```markdown
# 项目：<名称>

## 目标
- 

## 成功标准
- [ ] 

## 当前状态
- 

## 下一步（最多3条）
- [ ] 
- [ ] 
- [ ] 

## 相关资料
- [[...]]
```

Why this works: it keeps active work tied to outcome and prevents project plans from turning into archives of stale tasks.

### MOC note
Use when the user needs a topic entry page:

```markdown
# MOC：<主题名>

## 入口问题
- 我在这个主题最关心什么？

## 核心笔记
- [[观点1]]
- [[观点2]]
- [[观点3]]

## 项目关联
- [[项目A]]
- [[项目B]]

## 待补空白
- [ ] 
```

## High-value AI workflows

When the user asks how to actually use AI with the vault, suggest a small set of workflows instead of a giant prompt library.

### 1. Gap finding
Example prompt:

> 扫描 `02 Journal` 最近14天和 `03 Garden` 相关笔记，列出我在【主题】上的论证缺口、重复观点、未回答问题。输出成 checklist。

### 2. Link discovery
Example prompt:

> 基于 `99 MOCs/创作.md`，找出可互链但尚未链接的笔记对，按“新增链接价值”排序给前10条，并给出每条1句理由。

### 3. Promote Journal → Garden
Example prompt:

> 把 `02 Journal/` 最近的笔记里可沉淀的想法提炼成 3-5 条原子笔记草稿，写入 `03 Garden/_drafts/`，并保留原文引用位置。

### 4. Project planning from vault context
Example prompt:

> 进入 `04 Projects/项目X/`，根据 README 的目标和成功标准，给我“本周最小可交付计划”（3天版），每天最多2项任务。

## Recommended workflow cadence

If the user asks for a sustainable routine, recommend this minimum viable cadence:

### Daily
- Capture freely into Inbox or Journal
- Do not over-organize while thinking

### Weekly (15 minutes is enough)
- Clear Inbox
- Promote 3 useful ideas from Journal into Garden
- Add links to 1 MOC
- Keep only 3 next actions per active project

## How to respond

When using this skill, tailor the output to the user's need:

### If they ask for setup
Provide:
1. the folder structure
2. what goes in each folder
3. 1-3 starter templates
4. the first actions to take today

### If they ask for workflow design
Provide:
1. the operating model
2. the review cadence
3. 3-5 concrete prompts AI can run
4. likely failure modes and how to avoid them

### If they ask for critique
Evaluate their existing system against:
- simplicity
- retrieval ease
- separation of raw vs durable notes
- usefulness to AI
- maintenance burden

Then recommend the smallest set of changes that gives the biggest clarity gain.

## Failure modes to watch for

Flag these gently but clearly:
- Too many folders before enough notes exist
- Excessive tagging or metadata maintenance
- Turning Journal into a dumping ground that is never reviewed
- Garden notes that are just topic names with no claim
- Asking AI to write without enough source material
- Giving AI the whole vault when only one project or MOC is relevant

## Good defaults

If the user is unsure, steer toward:
- fewer folders
- fewer tags
- shorter templates
- stronger note titles
- explicit MOCs for major themes
- AI prompts grounded in actual vault paths

## Short answer style

When the user prefers brevity, compress the advice into:
- structure
- workflow
- 3 useful prompts
- first step

## Example first-step plan

If the user says “what should I do right now?”, give a plan like this:
1. Create the 6 top-level folders
2. Add one MOC for a current theme
3. Add one active project README
4. Create `03 Garden/_drafts/`
5. Ask the AI to identify the 3 most important missing notes
