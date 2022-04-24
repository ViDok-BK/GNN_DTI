import sys
import re

def get_ranges():
    t = [(24,27) ,(41,49) ,(140, 145), (163, 169) ,(188, 192)]
    ranges = []
    for i in t:
        ranges += [j for j in range(i[0], i[1]+1)]
    return ranges

def get_pocket(f_name_in, f_name_out, f_name_mapping, ranges):
    lines = open(f_name_in, 'r').readlines()
    chunked_lines = [[i for i in j.split(' ') if i!=''] for j in lines]
    pocket2protein_mapping = {}

    new_lines = []
    pocket_atom_cnt = 0
    protein_atom_cnt = 0
    for i, line in enumerate(chunked_lines):
        if line[0] not in ['ATOM', 'TER']:
            new_lines.append(lines[i])
        else:
            # Process pocket
            if re.search('^\d+$', line[5]) and int(line[5]) in ranges \
             or re.search('^\d+$', line[4]) and int(line[4]) in ranges:

                if line[0] == 'ATOM':
                    pocket2protein_mapping[pocket_atom_cnt] = protein_atom_cnt

                    pocket_atom_cnt += 1

                new_lines.append(lines[i])
            protein_atom_cnt += 1

    with open(f_name_out, 'w') as f:
        f.writelines(new_lines)

    print("Mapping:")
    print(pocket2protein_mapping)

    if f_name_mapping != "":
        with open(f_name_mapping, 'w') as f:
            f.write("pocket_idx,protein_noH_idx\n")
            for pk_idx, pr_idx in pocket2protein_mapping.items():
                f.write("%d,%d\n" % (pk_idx, pr_idx))

if __name__ == "__main__":
    ranges = get_ranges()
    print("Usage: python xxx.py protein_noH.pdb protein_pocket.pdb mapping_file")
    get_pocket(*sys.argv[1:], ranges)