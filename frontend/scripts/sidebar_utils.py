"""
Sidebar Utilities for KOKO Frontend
=====================================
Consolidated from: fix_sidebar.py, fix_sidebar_headers.py, fix_sidebar_legibility.py,
                   fix_sidebar_nesting.py, fix_sidebar_readability_v2.py, fix_sidebar_text.py,
                   improve_sidebar_text.py, increase_sidebar_subtext.py

Usage:
    python sidebar_utils.py [action]

Actions:
    --fix-headers     Increase sidebar section headers to text-base
    --fix-text        Increase sidebar content text size and improve contrast
    --fix-legibility  Add font-sans, remove italics, improve readability
    --fix-subtext     Increase Memory Engine subtext size
    --fix-all         Apply all sidebar fixes
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


def fix_headers(content):
    """Increase sidebar section headers from text-xs to text-base."""
    old_class = 'text-xs font-bold uppercase tracking-widest text-[#5d8c70]'
    new_class = 'text-base font-bold uppercase tracking-widest text-[#5d8c70]'
    
    if old_class in content:
        content = content.replace(old_class, new_class)
        print("✓ Headers updated to text-base")
    else:
        # Fallback regex
        content = re.sub(
            r'text-xs\s+font-bold\s+uppercase\s+tracking-widest\s+text-\[#5d8c70\]',
            new_class, content
        )
        print("✓ Headers updated (regex fallback)")
    return content


def fix_text_sizes(content):
    """Increase text sizes in sidebar lists and empty states."""
    replacements = [
        # List items
        ('text-xs bg-[#1e3326] p-2 rounded border border-[#3a5a45] text-slate-300 flex items-start gap-2',
         'text-sm bg-[#1e3326] p-3 rounded border border-[#3a5a45] text-slate-200 flex items-start gap-2 leading-relaxed'),
        # Empty states
        ('text-xs text-slate-500 italic', 'text-sm text-slate-400'),
        # Graph labels
        ('text-[8px] mt-1 text-slate-500', 'text-[10px] mt-1 text-slate-300 font-bold'),
        ('text-[10px] text-purple-300', 'text-xs text-purple-200'),
        ('text-[10px] text-blue-300', 'text-xs text-blue-200'),
        ('text-[10px] text-green-300', 'text-xs text-green-200'),
    ]
    
    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
    
    print(f"✓ Updated {count} text size(s)")
    return content


def fix_legibility(content):
    """Add font-sans, remove italics, improve overall legibility."""
    # Add font-sans to sidebar container
    if 'font-sans' not in content:
        content = content.replace('bg-[#14241b]/95', 'bg-[#14241b]/95 font-sans')
        print("✓ Added font-sans to sidebar")
    
    # Remove italics (carefully)
    italic_count = content.count('italic')
    content = content.replace(' italic', '')
    content = content.replace('italic ', '')
    print(f"✓ Removed {italic_count} italic occurrences")
    
    return content


def fix_subtext(content):
    """Increase Memory Engine subtext size."""
    sizes = [
        ('<p className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">Memory Engine</p>',
         '<p className="text-sm text-slate-400 font-mono tracking-widest uppercase">Memory Engine</p>'),
        ('<p className="text-xs text-slate-400 font-mono tracking-widest uppercase">Memory Engine</p>',
         '<p className="text-sm text-slate-400 font-mono tracking-widest uppercase">Memory Engine</p>'),
    ]
    
    for old, new in sizes:
        if old in content:
            content = content.replace(old, new)
            print("✓ Increased Memory Engine text size")
            return content
    
    print("✗ Memory Engine text not found")
    return content


def fix_all(content):
    """Apply all sidebar fixes in sequence."""
    content = fix_headers(content)
    content = fix_text_sizes(content)
    content = fix_legibility(content)
    content = fix_subtext(content)
    return content


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    action = sys.argv[1]
    content = load_file()
    
    actions = {
        '--fix-headers': fix_headers,
        '--fix-text': fix_text_sizes,
        '--fix-legibility': fix_legibility,
        '--fix-subtext': fix_subtext,
        '--fix-all': fix_all,
    }
    
    if action in actions:
        content = actions[action](content)
        save_file(content)
        print(f"\n✓ Sidebar update complete!")
    else:
        print(f"Unknown action: {action}")
        print(__doc__)


if __name__ == '__main__':
    main()
