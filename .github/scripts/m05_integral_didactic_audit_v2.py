from pathlib import Path

script_path = Path('.github/scripts/m05_integral_didactic_audit.py')
source = script_path.read_text(encoding='utf-8')

old_target = '"essa proporção é uma regra configurável do tutorial, e não"'
new_target = '"é uma regra configurável do tutorial, não uma intensidade ótima estimada."'
old_replacement = '"essa proporção é uma regra configurável desta análise, e não"'
new_replacement = '"é uma regra configurável desta análise, não uma intensidade ótima estimada."'

if source.count(old_target) != 1:
    raise SystemExit('M05 V2: Portuguese ranking target not unique')
if source.count(old_replacement) != 1:
    raise SystemExit('M05 V2: Portuguese ranking replacement not unique')

source = source.replace(old_target, new_target, 1)
source = source.replace(old_replacement, new_replacement, 1)

exec(compile(source, str(script_path), 'exec'))
