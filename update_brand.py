import os
import re

def update_templates():
    template_dir = 'templates'
    
    replacements = [
        (r'Soul Sip Cafe', '{{ BRAND_NAME }}'),
        (r'Soul Sip POS', '{{ BRAND_NAME }} POS'),
        (r'85113 21898', '{{ BRAND_MOBILE }}'),
        (r'Fresh Sips \&bull; Delicious Bites \&bull; Good Vibes', '{{ BRAND_TAGLINE }}'),
        (r'filename=''img/logo\.png''', "filename=BRAND_LOGO")
    ]
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                changed = False
                for old, new in replacements:
                    if re.search(old, content):
                        content = re.sub(old, new, content)
                        changed = True
                
                if changed:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {filepath}")

update_templates()