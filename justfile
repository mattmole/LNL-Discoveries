_default:
    just --list

# Build the site
build:
    uv run python3 rssScrapeMD3.py

# Check git status
gitStatus:
    git status


# Add indivudual fle to git
gitAdd file:
    git add {{file}} 

# Add all files to git
gitAddAll:
    git add *

# Commit to git
gitCommit:
    git commit

# Push to github
gitPush:
    git push
