# GitHub Publishing Guide

This document explains how to publish IntelliWealth to a new GitHub repository.

## What Should Be Committed

Commit:

- Source code
- Dockerfiles
- Docker Compose file
- Kubernetes manifests
- Monitoring configuration
- Documentation
- `.env.example`

Do not commit:

- `.env`
- AWS credentials
- SSH private keys
- `.pem` files
- `node_modules`
- Frontend `dist`
- Python virtual environments
- Local logs

The `.gitignore` file is configured for these cases.

## Check GitHub CLI

```bash
gh auth status
```

If the token is invalid, re-authenticate:

```bash
gh auth login -h github.com
```

Recommended choices:

```text
GitHub.com
HTTPS
Login with a web browser
```

## Initialize Git

From the project root:

```bash
git init
git add .
git status
```

Review files before committing.

Commit:

```bash
git commit -m "Initial IntelliWealth platform commit"
```

## Create A New GitHub Repository

Using GitHub CLI:

```bash
gh repo create intelliwealth \
  --private \
  --source . \
  --remote origin \
  --push
```

For a public repository:

```bash
gh repo create intelliwealth \
  --public \
  --source . \
  --remote origin \
  --push
```

## If Repository Name Already Exists

Use another name:

```bash
gh repo create intelliwealth-platform \
  --private \
  --source . \
  --remote origin \
  --push
```

## Push Future Changes

```bash
git add .
git commit -m "Describe the change"
git push
```

## Verify Remote

```bash
git remote -v
```

## Verify Published Repository

Open:

```text
https://github.com/<your-username>/<repo-name>
```
