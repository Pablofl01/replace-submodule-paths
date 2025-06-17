import os
import re
import glob
from git import Repo
from git.cmd import Git

def setup_safe_directories():
    """Configure Git to trust the workspace and its submodules."""
    git = Git()
    workspace = os.getcwd()
    
    # Set main workspace as safe
    git.config('--global', '--add', 'safe.directory', workspace)
    
    # Try to initialize repo to get submodules
    try:
        repo = Repo(workspace)
        # Set each submodule directory as safe
        for submodule in repo.submodules:
            submodule_path = os.path.join(workspace, submodule.path)
            git.config('--global', '--add', 'safe.directory', submodule_path)
    except Exception as e:
        print(f"Warning during safe directory setup: {e}")

def normalize_github_url(url):
    """Convert various GitHub URL formats to https format."""
    if 'git@github.com:' in url:
        url = url.replace('git@github.com:', 'https://github.com/')
    if url.startswith('git://'):
        url = url.replace('git://', 'https://')
    return url.rstrip('.git')  # Changed from replace to rstrip

def get_submodules():
    repo = Repo('.')
    submodules = {}
    
    for submodule in repo.submodules:
        path = submodule.path
        url = normalize_github_url(submodule.url)
        commit_hash = submodule.module().head.commit.hexsha
        submodules[path] = {'url': url, 'hash': commit_hash}
    
    return submodules

def update_markdown_links(content, submodules):
    pattern = r'\[([^\]]+)\]\(((?:\.{0,2}/[^\)]+)|(?:https://github\.com/[^/]+/[^/]+/(?:blob|tree)/[^/]+/[^\)]+))\)'
    
    def replace_link(match):
        text, path = match.groups()
        
        # Handle absolute GitHub URLs
        if path.startswith('https://github.com/'):
            for _, info in submodules.items():
                repo_url = info['url']
                if repo_url in path:
                    path_parts = path.split('/')
                    blob_index = path_parts.index('blob') if 'blob' in path_parts else path_parts.index('tree')
                    path_parts[blob_index + 1] = info['hash']
                    return f'[{text}]({"/".join(path_parts)})'
            return match.group(0)
        
        # Handle relative paths
        path = path.lstrip('./')
        for submodule_path, info in submodules.items():
            if path.startswith(submodule_path):
                remaining_path = path[len(submodule_path):].lstrip('/')
                # Remove redundant .git replacement since normalize_github_url already handles it
                return f'[{text}]({info["url"]}/tree/{info["hash"]}/{remaining_path})'
        
        return match.group(0)
    
    return re.sub(pattern, replace_link, content)

def process_markdown_files():
    setup_safe_directories()  # Call only once at the start
    submodules = get_submodules()
    file_pattern = os.environ.get('INPUT_FILE_PATTERN', '**/*.md')
    
    for filepath in glob.glob(file_pattern, recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            updated_content = update_markdown_links(content, submodules)
            
            if content != updated_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"Updated links in {filepath}")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == '__main__':
    process_markdown_files()