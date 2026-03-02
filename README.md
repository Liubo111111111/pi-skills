# pi-skills

A reusable skills collection project.

## Included Skills

- `skills/content-summary` (from `.claude/skills/content-summary`)
- `skills/url-to-markdown` (from `info-agent-plugin/utility-skills/url-to-markdown`)

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
    url-to-markdown/
  .github/workflows/auto-publish.yml
  README.md
```
