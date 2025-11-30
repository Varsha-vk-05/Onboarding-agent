from pathlib import Path
p = Path('.env')
if not p.exists():
    print('.env not found')
    raise SystemExit(1)
lines = p.read_text(encoding='utf-8').splitlines()
out = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith('OPENAI_API_KEY='):
        val = line.split('=',1)[1]
        j = i + 1
        # join subsequent lines that don't look like new variables or comments
        while j < len(lines) and not (lines[j].startswith('#') or '=' in lines[j]):
            val += lines[j].strip()
            j += 1
        out.append('OPENAI_API_KEY=' + val)
        i = j
    else:
        out.append(line)
        i += 1
# backup and write
p.with_suffix('.env.bak').write_text('\n'.join(out) + '\n', encoding='utf-8')
p.write_text('\n'.join(out) + '\n', encoding='utf-8')
print('Fixed .env and created .env.bak')
