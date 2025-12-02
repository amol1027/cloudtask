# Git Setup Instructions

## Branch Name
```
chore/project-setup
```

## Recommended Commit Message
```
chore: initial project scaffold with landing, accounts, tasks apps

- Created Django 5.x project with cloudtask configuration
- Added three apps: accounts, tasks, landing
- Configured Tailwind CSS via CDN
- Set up Whitenoise for static files
- Added PostgreSQL support with SQLite default
- Created landing page templates
- Configured timezone to Asia/Kolkata
- Added requirements.txt with pinned dependencies
- Created comprehensive .gitignore
```

## Git Commands

### Initialize Repository (if not already initialized)
```bash
git init
```

### Create and checkout the setup branch
```bash
git checkout -b chore/project-setup
```

### Stage all files
```bash
git add .
```

### Commit with the recommended message
```bash
git commit -m "chore: initial project scaffold with landing, accounts, tasks apps

- Created Django 5.x project with cloudtask configuration
- Added three apps: accounts, tasks, landing
- Configured Tailwind CSS via CDN
- Set up Whitenoise for static files
- Added PostgreSQL support with SQLite default
- Created landing page templates
- Configured timezone to Asia/Kolkata
- Added requirements.txt with pinned dependencies
- Created comprehensive .gitignore"
```

### Push to remote (if remote is configured)
```bash
git push -u origin chore/project-setup
```

## Verification

Verify your commit:
```bash
git log --oneline
git status
```

Check branch:
```bash
git branch
```
