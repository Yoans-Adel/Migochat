import ast
import os

def check_logic_errors(file_path):
    """Check for common logic errors"""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                # Check for comparison with True/False
                if isinstance(node, ast.Compare):
                    for comparator in node.comparators:
                        if isinstance(comparator, ast.Constant) and isinstance(comparator.value, bool):
                            errors.append(f'Line {node.lineno}: Comparing with True/False directly')
                
                # Check for mutable default arguments
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            errors.append(f'Line {node.lineno}: Mutable default argument in function {node.name}')
                
                # Check for except: pass (silent exceptions)
                if isinstance(node, ast.ExceptHandler):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        errors.append(f'Line {node.lineno}: Empty except block (silently catching exceptions)')
                
                # Check for == None instead of is None
                if isinstance(node, ast.Compare):
                    if isinstance(node.ops[0], ast.Eq):
                        for comp in node.comparators:
                            if isinstance(comp, ast.Constant) and comp.value is None:
                                errors.append(f'Line {node.lineno}: Use "is None" instead of "== None"')
    
    except SyntaxError as e:
        errors.append(f'Syntax Error: {e}')
    except Exception as e:
        errors.append(f'Error reading file: {e}')
    
    return errors

# Check main files
files_to_check = [
    'Server/routes/api.py',
    'Server/routes/webhook.py',
    'Server/routes/dashboard.py',
    'app/services/ai/gemini_service.py',
    'app/services/messaging/whatsapp_service.py',
    'app/services/messaging/messenger_service.py',
    'Server/main.py',
]

print('\n' + '='*70)
print('🔍 CHECKING FOR LOGIC ERRORS')
print('='*70 + '\n')

total_errors = 0
for file_path in files_to_check:
    if os.path.exists(file_path):
        errors = check_logic_errors(file_path)
        if errors:
            print(f'❌ {file_path}:')
            for error in errors[:10]:  # Show first 10 errors per file
                print(f'   {error}')
            print()
            total_errors += len(errors)
        else:
            print(f'✅ {file_path}: No logic errors found')
    else:
        print(f'⚠️  {file_path}: File not found')

print('\n' + '='*70)
if total_errors > 0:
    print(f'❌ Total logic errors found: {total_errors}')
else:
    print('✅ No logic errors found!')
print('='*70 + '\n')
