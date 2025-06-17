# Replace Submodule Paths

A GitHub Action that replaces relative links to submodules in markdown files with absolute GitHub URLs that point to the correct commit hash. This ensures that links to files in submodules remain valid even when the submodule is updated.

## What it does

- Finds all markdown files in your repository (configurable using `file_pattern`)
- Detects links to files in submodules
- Replaces relative paths with absolute GitHub URLs that include the current commit hash
- Updates existing absolute GitHub URLs to use the current commit hash

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `file_pattern` | Glob pattern for markdown files to process | No | `**/*.md` |

## Example Usage

```yaml
name: Update Submodule Links

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  update-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.2
        with:
          submodules: true
          
      - name: Update submodule links in markdown files
        uses: Pablofl01/replace-submodule-paths@v1
        with:
          file_pattern: "**/*.md"
          
      - uses: stefanzweifel/git-auto-commit-action@v6.0.1
        with:
          commit_message: "docs: update submodule links"
```

## Example transformations

From:
```markdown
[Link to file](./my-submodule/docs/readme.md)
[Link to file](https://github.com/owner/repo/blob/oldcommit/file.md)
```

To:
```markdown
[Link to file](https://github.com/owner/repo/tree/currentcommit/docs/readme.md)
[Link to file](https://github.com/owner/repo/blob/currentcommit/file.md)
```
