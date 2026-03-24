import re

def fix_view_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add imports if missing
    imports = "from django.utils.dateparse import parse_date\nfrom django.utils.timezone import make_aware\nfrom datetime import datetime, time\n"
    if 'from django.utils.dateparse import parse_date' not in content:
        content = content.replace("from django.db.models import", imports + "from django.db.models import", 1)

    # pattern to find the exact date filtering logic
    # Match:
    # date_filter = request.GET.get('date_filter')
    # if date_filter:
    #     queryset = queryset.filter(field__startswith=date_filter)
    
    # We'll do it manually to avoid bad regex matches
    def replacer(match):
        prefix = match.group(1) # e.g. "date_filter = request.GET.get('date_filter')\n"
        var = match.group(2) # e.g. "alerts"
        field = match.group(3) # e.g. "detected_at"
        
        # Look behind to find the exact indentation
        # The block format:
        # [indent]date_filter = request.GET.get('date_filter')
        # [indent]if date_filter:
        lines = prefix.split('\n')
        indent = ""
        for line in lines:
            if "if date_filter:" in line:
                indent = line.split("if date_filter:")[0]
                break
                
        replacement = (
            f"parsed_date = parse_date(date_filter)\n"
            f"{indent}if parsed_date:\n"
            f"{indent}    start_time = make_aware(datetime.combine(parsed_date, time.min))\n"
            f"{indent}    end_time = make_aware(datetime.combine(parsed_date, time.max))\n"
            f"{indent}    {var} = {var}.filter({field}__range=(start_time, end_time))"
        )
        return prefix.replace(f"{indent}if date_filter:\n", "") + replacement

    pattern = re.compile(
        r"([ \t]*date_filter = request\.GET\.get\('date_filter'\)\n[ \t]*if date_filter:\n[ \t]*)([a-zA-Z_0-9]+) = \2\.filter\(([a-zA-Z_0-9]+)__startswith=date_filter\)"
    )

    content_new = pattern.sub(replacer, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_new)
    print(f"Fixed {filepath}")

fix_view_file(r'd:\FlameGuard\officer_module\views.py')
fix_view_file(r'd:\FlameGuard\admin_module\views.py')
