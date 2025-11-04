with open('universities.csv','r',encoding='latin1') as f:
    raw_lines = [x.rstrip('\n\r') for x in f.readlines() if x.strip()]

print('RAW LINES (first 8):')
for i, ln in enumerate(raw_lines[:8], 1):
    print(i, repr(ln))

# strip surrounding quotes
lines = []
for ln in raw_lines:
    s = ln.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    lines.append(s)

print('\nSTRIPPED LINES (first 8):')
for i, ln in enumerate(lines[:8], 1):
    print(i, repr(ln))
    parts = ln.split(',')
    print('  parts_len=', len(parts), 'parts_repr=', [p for p in parts[:6]])
