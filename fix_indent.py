import re

def fix_view_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The issue:
    # parsed_date = parse_date(date_filter)
    #         if parsed_date:
    
    def replacer(match):
        indent = match.group(1)
        return f"{indent}parsed_date = parse_date(date_filter)\n{indent}if"
        
    content = re.sub(r"^parsed_date = parse_date\(date_filter\)\n([ \t]+)if", replacer, content, flags=re.MULTILINE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filepath}")

fix_view_file(r'd:\FlameGuard\officer_module\views.py')
fix_view_file(r'd:\FlameGuard\admin_module\views.py')
