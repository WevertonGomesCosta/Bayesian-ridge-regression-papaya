from pathlib import Path

script_path = Path('.github/scripts/m04_integral_didactic_audit.py')
script = script_path.read_text(encoding='utf-8')

old = 'usa o método com o menor `Mean_fold_RMSE`'
new = 'usa o método com a menor `Mean_fold_RMSE`'
count = script.count(old)
if count == 0:
    raise SystemExit('Expected Portuguese one-SE wording was not found in the audit script.')

script = script.replace(old, new)

exec(compile(script, str(script_path), 'exec'))
