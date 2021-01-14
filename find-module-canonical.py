unique_module_ids = {}
current_col = 'unknown'
with open('module-ids', 'r') as file:
    lines = file.readlines()
    for line in lines:
        if line.startswith('---'):
            current_col = line[4:].strip()
            continue
        module_id = line.strip()
        if module_id in unique_module_ids:
            continue
        unique_module_ids[module_id] = current_col
for module, canonical_book in unique_module_ids.items():
    print(f'{canonical_book} {module}')
