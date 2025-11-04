import pandas as pd

try:
    df = pd.read_csv('universities.csv', encoding='latin1', sep=None, engine='python')
except Exception:
    df = pd.read_csv('universities.csv', encoding='latin1')

if len(df.columns) != 5:
    with open('universities.csv', 'r', encoding='latin1') as f:
        raw_lines = [x.rstrip('\n\r') for x in f.readlines() if x.strip()]

    if not raw_lines:
        raise SystemExit('CSV is empty')

    # Strip surrounding quotes from lines if present, then split
    lines = []
    for ln in raw_lines:
        ln = ln.strip()
        if (ln.startswith('"') and ln.endswith('"')) or (ln.startswith("'") and ln.endswith("'")):
            ln = ln[1:-1]
        lines.append(ln)

    header_parts = lines[0].split(',')
    if len(header_parts) >= 5:
        data = [line.split(',') for line in lines]
        df = pd.DataFrame(data[1:], columns=data[0])
    else:
        parts = df.iloc[:, 0].str.split(',', expand=True)
        if parts.shape[1] >= 5:
            parts = parts.applymap(lambda v: v.strip().strip('"').strip("'") if isinstance(v, str) else v)
            df = parts.iloc[:, :5]
        else:
            raise SystemExit('Could not parse CSV into 5+ columns')

if len(df.columns) >= 5:
    df = df.iloc[:, :5]
    df.columns = ['name', 'country', 'city', 'website', 'fields']
else:
    raise SystemExit(f'CSV parsing failed: expected at least 5 columns but found {len(df.columns)}')

print('COLUMNS:', len(df.columns), df.columns.tolist())
print('\nSAMPLE ROW:', df.head(1).to_dict(orient='records'))
