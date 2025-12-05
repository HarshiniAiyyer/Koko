import sys
import os
import traceback

# Add backend to path
sys.path.append(os.getcwd())

try:
    print("=" * 60)
    print("Testing memory extraction...")
    print("=" * 60)
    
    from app.core.memory_engine.extraction.memory_extractor import extract_memory
    print("✓ Import successful")
    
    print("\nRunning extract_memory with test message...")
    result = extract_memory(["I feel stressed"])
    
    print("✓ Extraction successful!")
    print(f"\nResult:")
    print(f"  Preferences: {len(result.preferences)}")
    print(f"  Patterns: {len(result.patterns)}")
    print(f"  Facts: {len(result.facts)}")
    print(f"  Stats: {result.stats}")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("ERROR OCCURRED:")
    print("=" * 60)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
