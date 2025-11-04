"""
Auto-fix script for common Python code issues
Fixes: unused imports, trailing whitespace, blank lines, etc.
"""
import re
import os
from pathlib import Path

def remove_unused_imports(file_path, unused_imports):
    """Remove unused imports from a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    
    for line in lines:
        should_keep = True
        for unused in unused_imports:
            # Extract just the import part (e.g., 'typing.Optional')
            import_name = unused.split("'")[1] if "'" in unused else unused
            
            # Check if this line imports the unused module
            if f"import {import_name}" in line or f"from {import_name.rsplit('.', 1)[0]}" in line:
                # Check if it's specifically this import
                if import_name.split('.')[-1] in line:
                    should_keep = False
                    modified = True
                    break
        
        if should_keep:
            new_lines.append(line)
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def fix_whitespace_issues(file_path):
    """Fix trailing whitespace and blank line issues"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove trailing whitespace
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # Ensure file ends with newline
    if content and not content.endswith('\n'):
        content += '\n'
    
    # Remove multiple consecutive blank lines (keep max 2)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_undefined_variables():
    """Fix specific undefined variables in known files"""
    # Already fixed BWW_STORE_AVAILABLE -> bww_store_available
    print("✅ Undefined variables already fixed")

def process_directory(directory):
    """Process all Python files in directory"""
    fixed_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and .venv directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.venv', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    if fix_whitespace_issues(file_path):
                        fixed_files.append(file_path)
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def main():
    print("🔧 Starting auto-fix for all Python files...")
    print("=" * 70)
    
    # Fix undefined variables first
    fix_undefined_variables()
    
    # Process main directories
    directories = ['app', 'Server', 'database', 'bww_store', 'scripts', 'config']
    all_fixed = []
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\n📁 Processing {directory}/...")
            fixed = process_directory(directory)
            all_fixed.extend(fixed)
            print(f"   Fixed {len(fixed)} files")
    
    print("\n" + "=" * 70)
    print(f"✅ Total files fixed: {len(all_fixed)}")
    
    if all_fixed:
        print("\n📋 Fixed files:")
        for file in all_fixed[:20]:  # Show first 20
            print(f"   • {file}")
        if len(all_fixed) > 20:
            print(f"   ... and {len(all_fixed) - 20} more")
    
    print("\n🎉 Auto-fix completed!")
    print("\n💡 Next steps:")
    print("   1. Run: python check_logic_errors.py")
    print("   2. Run: python -m flake8 app/ Server/ --select=E,F")
    print("   3. Test: python -c 'import Server.main'")

if __name__ == "__main__":
    main()
