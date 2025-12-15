import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
import hashlib

# Configuration
ASSETS_DIR = Path('assets')
IMAGES_DIR = ASSETS_DIR / 'images'
FONTS_DIR = ASSETS_DIR / 'fonts'
OTHERS_DIR = ASSETS_DIR / 'others'

# Create directories
for directory in [IMAGES_DIR, FONTS_DIR, OTHERS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Mappings to avoid re-downloading
url_to_local_path = {}

def get_extension(url):
    path = urllib.parse.urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    if not ext:
        return ''
    return ext

def get_target_dir(ext):
    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico']:
        return IMAGES_DIR
    elif ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']:
        return FONTS_DIR
    else:
        return OTHERS_DIR

def download_file(url):
    if url in url_to_local_path:
        return url_to_local_path[url]

    try:
        ext = get_extension(url)
        # Create a safe filename from the URL hash to ensure uniqueness but short names
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]
        
        # Try to keep original filename if possible/reasonable
        original_name = os.path.basename(urllib.parse.urlparse(url).path)
        # Remove weird characters from original name
        original_name = re.sub(r'[^a-zA-Z0-9._-]', '', original_name)
        
        if not original_name or len(original_name) > 50:
             filename = f"{url_hash}{ext}"
        else:
            # If original name doesn't have the hash, maybe prepend it to be safe from collisions
            # But Framer usually has hashy names anyway.
            filename = original_name

        target_dir = get_target_dir(ext)
        local_path = target_dir / filename
        
        # Relative path for HTML (assuming assets is in root)
        # We need to calculate relative path based on the file we are editing, 
        # BUT simplest is to use absolute path from root site, i.e., /assets/...
        # or relative.
        # Let's use relative paths. For now, we store the Path object.

        if not local_path.exists():
            print(f"Downloading: {url} -> {local_path}")
            # User agent to avoid some blockers (though framer assets usually public)
            req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req) as response:
                with open(local_path, 'wb') as f:
                    f.write(response.read())
        else:
            print(f"Skipping (exists): {local_path}")

        url_to_local_path[url] = local_path
        return local_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def process_file(file_path):
    print(f"Processing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Warning: Could not read {file_path} as UTF-8. Skipping.")
        return

    # Regex to find Framer URLs
    # Looking for https://framerusercontent.com followed by valid url characters until quote or parenthesis or space
    # Common contexts: src="...", href="...", url(...), srcset="..."
    
    # We will use a reasonably generous regex but exclude trailing quotes/parens
    # Broader regex to capture everything until common delimiters
    framer_url_pattern = r'https://framerusercontent\.com/[^"\'\)\s]+'
    
    matches = set(re.findall(framer_url_pattern, content))
    print(f"Found {len(matches)} matches in {file_path}")
    
    new_content = content
    
    # Sort matches by length descending to replace longest first (in case of overlaps, though unlikely with this regex)
    sorted_matches = sorted(matches, key=len, reverse=True)
    
    import html
    
    for url in sorted_matches:
        url = html.unescape(url)

        # Check if it's a valid asset to download
        # Ignore some metadata urls maybe?
        if 'searchIndex' in url:
            continue
            
        local_path_obj = download_file(url)
        if local_path_obj:
            # Calculate relative path from current file to the asset
            # file_path is e.g. Contact/page.html
            # local_path_obj is e.g. assets/images/funny.jpg
            
            # relpath needs absolute paths or consistent relative reference
            # Let's operate on full resolved paths
            abs_file_path = file_path.resolve()
            abs_asset_path = local_path_obj.resolve()
            
            try:
                rel_path = os.path.relpath(abs_asset_path, abs_file_path.parent)
                # Ensure forward slashes for URLs
                rel_path = rel_path.replace(os.sep, '/')
                
                # Replace in content
                # We simply replace the string. 
                new_content = new_content.replace(url, rel_path)
            except ValueError:
                # Should not happen on same drive
                print(f"Error calculating relative path for {url}")

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes for: {file_path}")

def main():
    root_dir = Path('.')
    html_files = list(root_dir.rglob('*.html'))
    
    for html_file in html_files:
        process_file(html_file)

    print("Migration complete!")

if __name__ == "__main__":
    main()
