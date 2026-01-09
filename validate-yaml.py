import os
import sys
from pathlib import Path

try:
	import yaml
except Exception as error:  # pragma: no cover
	print('[yaml] PyYAML not installed')
	print('      Install with: python -m pip install -r requirements.txt')
	print(f'      Details: {error}')
	sys.exit(1)


def find_yaml_files(root_dir: Path) -> list[Path]:
	results: list[Path] = []
	for current_root, dirnames, filenames in os.walk(root_dir):
		# Skip node_modules and hidden folders
		dirnames[:] = [
			d for d in dirnames
			if d != 'node_modules' and not d.startswith('.')
		]

		for filename in filenames:
			lower = filename.lower()
			if lower.endswith('.yaml') or lower.endswith('.yml'):
				results.append(Path(current_root) / filename)
	return sorted(results)


def validate_yaml_file(file_path: Path) -> tuple[bool, str | None]:
	try:
		text = file_path.read_text(encoding='utf-8')
		yaml.safe_load(text)
		return True, None
	except Exception as error:
		return False, str(error)


def main() -> int:
	root_dir = Path.cwd()
	yaml_files = find_yaml_files(root_dir)

	failures: list[tuple[Path, str]] = []
	for file_path in yaml_files:
		ok, message = validate_yaml_file(file_path)
		if not ok:
			failures.append((file_path, message or 'Unknown error'))

	if not failures:
		print(f'[yaml] OK: {len(yaml_files)} files')
		return 0

	print(f'[yaml] FAILED: {len(failures)}/{len(yaml_files)} files')
	for file_path, message in failures:
		relative = file_path.relative_to(root_dir).as_posix()
		print(f'\n- {relative}')
		print(message)

	return 1


if __name__ == '__main__':
	raise SystemExit(main())
