from pathlib import Path

script_path = Path('.github/scripts/m04_integral_didactic_audit.py')
script = script_path.read_text(encoding='utf-8')

replacements = [
    (
        'usa o método com o menor `Mean_fold_RMSE`',
        'usa o método com a menor `Mean_fold_RMSE`',
        'Portuguese one-SE anchor',
    ),
    (
        'These correlations describe associations among OOF genomic values produced by the selected method for each trait. Since different traits may use different methods and the values are cross-fitted, the matrix summarizes association among predicted scores rather than jointly estimated genetic covariance. It therefore should not be interpreted as a genetic-correlation matrix from a multivariate model.',
        'These correlations describe associations among the OOF genomic values produced by the selected method for each trait. Because different traits may use different methods and the values are cross-fitted, the matrix summarizes associations among predictive scores rather than jointly estimated genetic covariance. It should therefore not be interpreted as a genetic-correlation matrix from a multivariate model.',
        'English correlation anchor',
    ),
]

for old, new, label in replacements:
    count = script.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one script target, found {count}')
    script = script.replace(old, new, 1)

old_loop = '''for lang, path in FILES.items():
    original = path.read_text(encoding="utf-8")
    revised = revise_pt(original) if lang == "pt" else revise_en(original)
    validate(revised, lang.upper())
    path.write_text(revised, encoding="utf-8", newline="\\n")

print("Module 04 didactic revision applied to PT/EN sources.")
'''

new_loop = '''revised_files = {}
for lang, path in FILES.items():
    original = path.read_text(encoding="utf-8")
    revised = revise_pt(original) if lang == "pt" else revise_en(original)
    validate(revised, lang.upper())
    revised_files[path] = revised

# Atomic at the source-file level: write only after both languages pass.
for path, revised in revised_files.items():
    path.write_text(revised, encoding="utf-8", newline="\\n")

print("Module 04 didactic revision applied to PT/EN sources.")
'''

count = script.count(old_loop)
if count != 1:
    raise SystemExit(f'Atomic-write loop: expected exactly one script target, found {count}')
script = script.replace(old_loop, new_loop, 1)

exec(compile(script, str(script_path), 'exec'))
