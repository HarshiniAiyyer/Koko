"""
Header & Branding Utilities for KOKO Frontend
===============================================
Consolidated from: refine_header.py, redesign_header.py, update_header_sidebar.py,
                   improve_subtitle.py

Usage:
    python header_utils.py [action]

Actions:
    --update-branding     Change header text to "KOKO - The Personality Engine"
    --add-subtitle-span   Style subtitle as inline span (smaller, lighter)
    --vertical-layout     Redesign header to vertical stack layout
    --improve-subtitle    Increase subtitle readability (size, opacity)
    --fix-all             Apply vertical layout with readable subtitle
"""

import os
import sys

FILE_PATH = os.path.join(os.path.dirname(__file__), '../src/App.jsx')


def load_file():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(content):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def update_branding(content):
    """Change header from 'The Companion' to 'The Personality Engine'."""
    old = 'KOKO <span className="text-slate-500 text-sm tracking-normal normal-case font-sans opacity-50">| The Companion</span>'
    new = 'KOKO - The Personality Engine'
    
    if old in content:
        content = content.replace(old, new)
        print("✓ Updated header to 'KOKO - The Personality Engine'")
    else:
        print("✗ Could not find original header text")
    return content


def add_subtitle_span(content):
    """Style subtitle as inline span (smaller, lighter colors)."""
    old = 'KOKO - The Personality Engine'
    new = 'KOKO <span className="text-base text-slate-400 tracking-normal normal-case font-sans ml-2">- The Personality Engine</span>'
    
    if old in content:
        content = content.replace(old, new)
        print("✓ Added styled subtitle span")
    else:
        print("✗ Could not find header text to style")
    return content


def vertical_layout(content):
    """Redesign header to vertical stack layout (KOKO on top, subtitle below)."""
    old_block = '''                        <h1 className="font-cinzel font-bold text-2xl tracking-[0.15em] text-yellow-500">
                            KOKO <span className="text-base text-slate-400 tracking-normal normal-case font-sans ml-2">- The Personality Engine</span>
                        </h1>'''
    
    new_block = '''                        <div className="flex flex-col">
                            <h1 className="font-cinzel font-bold text-2xl tracking-[0.15em] text-yellow-500 leading-none">
                                KOKO
                            </h1>
                            <p className="text-xs text-yellow-600/60 tracking-[0.2em] font-cinzel uppercase mt-1">
                                The Personality Engine
                            </p>
                        </div>'''
    
    if old_block in content:
        content = content.replace(old_block, new_block)
        print("✓ Redesigned header to vertical stack layout")
    else:
        # Try alternative patterns
        if 'KOKO - The Personality Engine' in content:
            print("✗ Header found but structure doesn't match - try --add-subtitle-span first")
        else:
            print("✗ Could not find header structure")
    return content


def improve_subtitle(content):
    """Increase subtitle readability (larger size, higher opacity)."""
    old = '<p className="text-xs text-yellow-600/60 tracking-[0.2em] font-cinzel uppercase mt-1">'
    new = '<p className="text-sm text-yellow-500/85 tracking-[0.15em] font-cinzel uppercase mt-1">'
    
    if old in content:
        content = content.replace(old, new)
        print("✓ Increased subtitle readability")
    else:
        print("✗ Could not find subtitle element")
    return content


def fix_all(content):
    """Apply vertical layout with readable subtitle."""
    # Check current state and apply appropriate fixes
    if '| The Companion' in content:
        content = update_branding(content)
        content = add_subtitle_span(content)
        content = vertical_layout(content)
    elif 'KOKO - The Personality Engine' in content and '<span' not in content.split('KOKO')[1][:100]:
        content = add_subtitle_span(content)
        content = vertical_layout(content)
    
    content = improve_subtitle(content)
    return content


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    action = sys.argv[1]
    content = load_file()
    
    actions = {
        '--update-branding': update_branding,
        '--add-subtitle-span': add_subtitle_span,
        '--vertical-layout': vertical_layout,
        '--improve-subtitle': improve_subtitle,
        '--fix-all': fix_all,
    }
    
    if action in actions:
        content = actions[action](content)
        save_file(content)
        print(f"\n✓ Header update complete!")
    else:
        print(f"Unknown action: {action}")
        print(__doc__)


if __name__ == '__main__':
    main()
