---
name: setup-workspace
description: Execution mode - Bootstraps the Resume Writer environment, installs dependencies, and ensures the user safely configures their private cv-data repository. Use this when a user first clones the repository or asks to "run setup" or "setup my environment".
---

# Setup Workspace Skill

This skill guides a new user through installing dependencies and securing their personal data. 

## Phase 1: Dependency Installation
Run the local setup script using the shell execution tool:

```bash
./setup.sh
```

## Phase 2: Security Assessment
Analyze the output of the `setup.sh` script. 

If the script outputs `[CODEX_HOOK: SUBMODULE_RECOMMENDED]`, you MUST pause execution and initiate the Submodule Creation Walkthrough.

### Submodule Creation Walkthrough
If the hook is detected, speak to the user directly with a strong security warning. Explain that `cv-data` will house all their personal information (phone, address, detailed work history) and it is incredibly dangerous to leave it in the main repository, where an accidental `git push` could publish it to GitHub.

Ask the user if they would like you to help them transition `cv-data` into a private submodule. 

If they say YES, perform the following steps sequentially, interacting with the user as needed:

1. **Ask for Git Remote:** Ask the user to create an empty, **PRIVATE** repository on GitHub, GitLab, or Gitea, and provide you with the SSH or HTTPS remote URL (e.g., `git@github.com:username/my-cv-data.git`).
2. **Move existing data out of the way:**
   ```bash
   mv cv-data cv-data-backup
   ```
3. **Add the new submodule:**
   ```bash
   git submodule add <USER_PROVIDED_URL> cv-data
   ```
4. **Copy data back:**
   ```bash
   cp -r cv-data-backup/* cv-data/
   ```
5. **Initialize the new private repository:**
   ```bash
   cd cv-data
   git add .
   git commit -m "Initial commit of private CV data"
   git push -u origin main
   cd ..
   ```
6. **Commit the submodule link to the main repo:**
   ```bash
   git add .gitmodules cv-data
   git commit -m "Securely transition cv-data to a private submodule"
   ```
7. **Clean up:**
   ```bash
   rm -rf cv-data-backup
   ```

Confirm with the user that their data is now safe.