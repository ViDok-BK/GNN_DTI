import os

MAPPING_FILE = "../vidok/pocket_to_protein_mapping.csv"

result_files = os.listdir('./')
result_files = list(filter(lambda x: x.endswith('.csv'), result_files))

mapping = {}
with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()[1:]
    for line in lines:
        pocket_i, protein_i = line.strip().split(',')
        mapping[pocket_i] = protein_i

for rf in result_files:
    lines = []
    with open(rf, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i == 0: continue
            chunked_line = line.strip().split(',')
            chunked_line[1] = mapping[chunked_line[1]]
            lines[i] = ','.join(chunked_line)
    
    with open('converted/' + rf, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        