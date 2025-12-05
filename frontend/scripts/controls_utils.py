"""
Icons & Buttons Utilities for KOKO Frontend
=============================================
Consolidated from: apply_red_black.py, update_icons_solid.py, update_ui_controls.py,
                   enhance_show_raw.py, move_new_deal.py, align_buttons.py

Usage:
    python controls_utils.py [action]

Actions:
    --enlarge-icons       Make persona icons larger (w-12 h-12, size=20)
    --solid-fill          Apply solid fill to icons with real card colors
    --red-black-scheme    Apply red/black color scheme to icons and button
    --enhance-show-raw    Make Show Raw button more visible
    --move-new-deal       Move New Deal button below persona icons
    --align-footer        Align New Deal with Deal Cards button (bottom)
    --fix-all             Apply all icon/button improvements
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


def enlarge_icons(content):
    """Increase persona icon sizes."""
    replacements = [
        ('w-8 h-8 rounded-full', 'w-12 h-12 rounded-full'),
        ('<tone.icon size={14} />', '<tone.icon size={20} />'),
        ('gap-2', 'gap-3'),  # In the icon container
    ]
    
    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new, 1)  # Only first occurrence
            count += 1
    
    print(f"✓ Enlarged {count} icon element(s)")
    return content


def solid_fill_icons(content):
    """Apply solid fill to icons with classic card suit colors."""
    start_marker = '{Object.values(TONES).map(tone => ('
    end_marker = '))}'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("✗ Could not find icon map block")
        return content
    
    end_idx = content.find(end_marker, start_idx) + 3
    
    new_map_body = '''{Object.values(TONES).map(tone => (
                                                <button
                                                    key={tone.id}
                                                    onClick={() => switchFinalTone(tone.id)}
                                                    className={`w-14 h-14 rounded-full flex items-center justify-center border-2 transition-all duration-300 shadow-sm ${selectedTone === tone.id ? 'bg-white border-slate-900 scale-110 shadow-xl ring-2 ring-slate-900 z-10' : 'bg-white border-slate-200 hover:border-slate-400 hover:scale-105'}`}
                                                    title={tone.label}
                                                >
                                                    <tone.icon size={28} className={tone.realColor} fill="currentColor" strokeWidth={1.5} />
                                                </button>
                                            ))}'''
    
    content = content[:start_idx] + new_map_body + content[end_idx:]
    print("✓ Applied solid fill to icons with card suit colors")
    return content


def red_black_scheme(content):
    """Apply red/black color scheme to icons and New Deal button."""
    replacements = [
        # Icon selected state
        ("bg-slate-800 text-white border-slate-800 scale-110 shadow-lg' : 'bg-white text-slate-400 border-slate-200 hover:border-slate-400 hover:scale-105",
         "bg-black text-red-600 border-red-600 scale-110 shadow-lg shadow-red-900/20' : 'bg-white text-slate-400 border-slate-200 hover:border-red-300 hover:text-red-400 hover:scale-105"),
        # New Deal button
        ('bg-slate-800 hover:bg-slate-900 text-white',
         'bg-[#8b0000] hover:bg-[#a00000] text-[#fdfbf7]'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✓ Applied red/black scheme")
    
    return content


def enhance_show_raw(content):
    """Make Show Raw button more visible."""
    old = 'className="text-xs uppercase tracking-wider font-bold text-slate-400 hover:text-slate-600 px-2 py-1 border border-slate-200 rounded"'
    new = 'className="text-xs uppercase tracking-wider font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 px-4 py-2 rounded transition-all shadow-sm hover:shadow"'
    
    if old in content:
        content = content.replace(old, new)
        print("✓ Enhanced Show Raw button visibility")
    else:
        print("✗ Could not find Show Raw button")
    return content


def move_new_deal(content):
    """Move New Deal button below persona icons (vertical layout)."""
    old_footer = '<div className="mt-8 pt-6 border-t border-slate-100 flex justify-between items-center">'
    new_footer = '<div className="mt-8 pt-6 border-t border-slate-100 flex flex-col items-center gap-6">'
    
    if old_footer in content:
        content = content.replace(old_footer, new_footer)
        content = content.replace('<div className="flex gap-3">', '<div className="flex gap-6 justify-center w-full">', 1)
        print("✓ Moved New Deal button below icons")
    else:
        print("✗ Could not find footer container")
    return content


def align_footer(content):
    """Align footer elements at the bottom of the card."""
    replacements = [
        # Content area to flex-1
        ('className="prose prose-slate max-w-none font-serif text-lg leading-relaxed text-slate-700 overflow-y-auto max-h-[400px] pr-2 custom-scrollbar"',
         'className="flex-1 prose prose-slate max-w-none font-serif text-lg leading-relaxed text-slate-700 overflow-y-auto pr-2 custom-scrollbar"'),
        # Footer padding
        ('<div className="mt-8 pt-6 border-t border-slate-100 flex flex-col items-center gap-6">',
         '<div className="mt-4 pt-6 border-t border-slate-100 flex flex-col items-center gap-6 pb-2">'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
    
    print("✓ Aligned footer at bottom")
    return content


def fix_all(content):
    """Apply all icon/button improvements."""
    content = solid_fill_icons(content)
    content = enhance_show_raw(content)
    content = move_new_deal(content)
    content = align_footer(content)
    return content


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    action = sys.argv[1]
    content = load_file()
    
    actions = {
        '--enlarge-icons': enlarge_icons,
        '--solid-fill': solid_fill_icons,
        '--red-black-scheme': red_black_scheme,
        '--enhance-show-raw': enhance_show_raw,
        '--move-new-deal': move_new_deal,
        '--align-footer': align_footer,
        '--fix-all': fix_all,
    }
    
    if action in actions:
        content = actions[action](content)
        save_file(content)
        print(f"\n✓ Controls update complete!")
    else:
        print(f"Unknown action: {action}")
        print(__doc__)


if __name__ == '__main__':
    main()
