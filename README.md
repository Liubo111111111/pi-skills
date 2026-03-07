# pi-skills

A reusable skills collection project.

## Included Skills

- `skills/content-summary` (from `.claude/skills/content-summary`)
- `skills/url-to-markdown` (from `info-agent-plugin/utility-skills/url-to-markdown`)
- `skills/openclaw-bailian-coding-fix`
- `skills/openclaw-dual-feishu-bots`
- `skills/openclaw-no-reply-fix`

## Quick Start

```bash
git clone <your-repo-url>
cd pi-skills
```

## Auto Publish

This repository includes a GitHub Actions workflow that automatically creates a release on every push to `main`.

- Workflow file: `.github/workflows/auto-publish.yml`
- Release tag format: `auto-<run_number>`

## Structure

```text
pi-skills/
  skills/
    content-summary/
    openclaw-bailian-coding-fix/
    openclaw-dual-feishu-bots/
    openclaw-no-reply-fix/
    url-to-markdown/
  .github/workflows/auto-publish.yml
  README.md
```
