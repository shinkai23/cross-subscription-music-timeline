# GitHub Setup

The local repository is ready. The current environment does not have the GitHub CLI installed, and no remote is configured yet.

## Recommended Repository Settings

- Repository name: `cross-subscription-music-timeline`
- Visibility: public for portfolio, private until provider keys and app IDs are separated
- Default branch: `main`
- Enable Issues
- Enable Projects
- Require PR before merge after the first push

## Manual Remote Setup

After creating the repository on GitHub:

```bash
git remote add origin https://github.com/<owner>/cross-subscription-music-timeline.git
git push -u origin main
```

## Suggested Labels

- `feature`
- `bug`
- `ios`
- `android`
- `backend`
- `apple-music`
- `spotify`
- `matching`
- `moderation`
- `ai`
- `legal-risk`
- `research`

## First Issues

Use [GitHub Backlog](github-backlog.md) to create the initial issues.
