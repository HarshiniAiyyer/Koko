"""
Layout Utilities for KOKO Frontend
====================================
Consolidated from: fix_layout_v2.py, enlarge_layout.py, update_label_colors.py

Usage:
    python layout_utils.py [action]

Actions:
    --enlarge-grid        Increase main grid height (600px → 800px)
    --enlarge-text        Increase text sizes in cards
    --update-labels       Update "Your Hand" and "The Reveal" label colors
    --add-scale           Add zoom scale to main grid
    --remove-scale        Remove zoom scale from main grid
    --fix-all             Apply grid enlargement and label colors
"""

import os
import re
import sys

FILE_PATH = os.path.join(os.path.dirname(__file__), '../src/App.jsx')


def load_file():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(content):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def enlarge_grid(content):
    """Increase main grid container height."""
    replacements = [
        ('h-[600px]', 'h-[800px]'),
        ('h-[500px]', 'h-[600px]'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Increased grid height: {old} → {new}")
            break
    else:
        print("✗ Could not find grid height to enlarge")
    
    return content


def enlarge_text(content):
    """Increase text sizes in cards."""
    replacements = [
        ('text-slate-800 text-lg font-playfair', 'text-slate-800 text-xl font-playfair'),
        ('font-playfair font-bold text-2xl text-slate-800', 'font-playfair font-bold text-3xl text-slate-800'),
    ]
    
    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    print(f"✓ Enlarged {count} text element(s)")
    return content


def update_label_colors(content):
    """Update 'Your Hand' and 'The Reveal' label colors to be more readable."""
    old_container = 'text-[#5d8c70] opacity-60'
    new_container = 'text-[#8ab090]'
    old_line = 'bg-[#5d8c70]'
    new_line = 'bg-[#8ab090]'
    
    def update_block(text, marker):
        idx = text.find(marker)
        if idx == -1:
            return text
        
        container_start = text.rfind('<div className="flex items-center gap-4', 0, idx)
        container_end = text.find('</div>', idx) + 6
        
        if container_start == -1:
            return text
        
        block = text[container_start:container_end]
        new_block = block.replace(old_container, new_container)
        new_block = new_block.replace(old_line, new_line)
        
        return text[:container_start] + new_block + text[container_end:]
    
    content = update_block(content, 'YOUR HAND')
    content = update_block(content, 'THE REVEAL')
    print("✓ Updated label colors to #8ab090")
    return content


def add_scale(content):
    """Add zoom scale transform to main grid."""
    pattern = r'(grid grid-cols-1 (?:md|lg):grid-cols-2 gap-\d+ (?:lg:)?gap-\d+ w-full max-w-\d+xl px-\d+ pb-\d+ h-\[\d+px\])'
    
    if 'scale-105' not in content:
        content = re.sub(pattern, r'\1 transform scale-105 origin-center', content)
        print("✓ Added scale-105 to main grid")
    else:
        print("✗ Scale already applied")
    
    return content


def remove_scale(content):
    """Remove zoom scale transform from main grid."""
    content = content.replace(' transform scale-105 origin-center', '')
    print("✓ Removed scale transform")
    return content


def fix_all(content):
    """Apply grid enlargement and label colors."""
    content = enlarge_grid(content)
    content = update_label_colors(content)
    return content


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    action = sys.argv[1]
    content = load_file()
    
    actions = {
        '--enlarge-grid': enlarge_grid,
        '--enlarge-text': enlarge_text,
        '--update-labels': update_label_colors,
        '--add-scale': add_scale,
        '--remove-scale': remove_scale,
        '--fix-all': fix_all,
    }
    
    if action in actions:
        content = actions[action](content)
        save_file(content)
        print(f"\n✓ Layout update complete!")
    else:
        print(f"Unknown action: {action}")
        print(__doc__)


if __name__ == '__main__':
    main()
