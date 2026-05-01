from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
	import yaml
except Exception as error:  # pragma: no cover
	print('[parity] PyYAML not installed')
	print('         Install with: python -m pip install -r requirements.txt')
	print(f'         Details: {error}')
	sys.exit(1)


@dataclass(slots=True)
class LocaleFile:
	scalars: dict[str, str] = field(default_factory=dict)
	sequences: dict[str, list[str]] = field(default_factory=dict)
	unsupported_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FileReport:
	path: str
	missing_keys: list[str] = field(default_factory=list)
	extra_keys: list[str] = field(default_factory=list)
	kind_mismatches: list[str] = field(default_factory=list)
	unsupported_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class LocaleReport:
	code: str
	missing_files: list[str] = field(default_factory=list)
	extra_files: list[str] = field(default_factory=list)
	files: list[FileReport] = field(default_factory=list)


def load_yaml_file(file_path: Path) -> dict[str, Any]:
	text = file_path.read_text(encoding='utf-8')
	loaded = yaml.safe_load(text)
	if loaded is None:
		return {}
	if not isinstance(loaded, dict):
		raise TypeError(f'{file_path.name} root must be a YAML mapping')
	loaded.pop('meta', None)
	return loaded


def is_scalar_value(value: Any) -> bool:
	return isinstance(value, (str, int, float, bool))


def flatten_yaml(
	value: Any,
	prefix: str,
	scalars: dict[str, str],
	sequences: dict[str, list[str]],
	unsupported_paths: list[str],
) -> None:
	if isinstance(value, dict):
		for key, nested in value.items():
			full_key = str(key) if not prefix else f'{prefix}.{key}'
			flatten_yaml(nested, full_key, scalars, sequences, unsupported_paths)
		return

	if isinstance(value, list):
		if all(is_scalar_value(item) for item in value):
			sequences[prefix] = [str(item) for item in value]
		else:
			unsupported_paths.append(prefix)
		return

	if is_scalar_value(value):
		scalars[prefix] = str(value)
		return

	if value is None:
		return

	unsupported_paths.append(prefix)


def read_locale_files(locale_dir: Path) -> dict[str, LocaleFile]:
	files: dict[str, LocaleFile] = {}
	for file_path in sorted(locale_dir.glob('*.yaml')):
		loaded = load_yaml_file(file_path)
		scalars: dict[str, str] = {}
		sequences: dict[str, list[str]] = {}
		unsupported_paths: list[str] = []
		flatten_yaml(loaded, '', scalars, sequences, unsupported_paths)
		files[file_path.name] = LocaleFile(
			scalars=scalars,
			sequences=sequences,
			unsupported_paths=sorted(set(path for path in unsupported_paths if path)),
		)
	return files


def diff_keys(left: dict[str, str], right: dict[str, str]) -> list[str]:
	return sorted(key for key in left if key not in right)


def build_kind_map(locale_file: LocaleFile) -> dict[str, str]:
	kinds = {key: 'scalar' for key in locale_file.scalars}
	kinds.update({key: 'sequence' for key in locale_file.sequences})
	return kinds


def locale_file_name(english_file_name: str, locale_code: str) -> str:
	if english_file_name == 'en.yaml':
		return f'{locale_code}.yaml'
	return english_file_name


def audit_translations(root_dir: Path) -> list[LocaleReport]:
	english_dir = root_dir / 'en'
	english_files = read_locale_files(english_dir)

	reports: list[LocaleReport] = []
	for locale_dir in sorted(
		path for path in root_dir.iterdir()
		if path.is_dir() and path.name != 'en' and not path.name.startswith('.')
	):
		locale_files = read_locale_files(locale_dir)
		report = LocaleReport(code=locale_dir.name)

		for file_name, english_file in english_files.items():
			expected_file_name = locale_file_name(file_name, locale_dir.name)
			locale_file = locale_files.get(expected_file_name)
			if locale_file is None:
				report.missing_files.append(expected_file_name)
				continue

			english_kinds = build_kind_map(english_file)
			locale_kinds = build_kind_map(locale_file)

			file_report = FileReport(
				path=expected_file_name,
				missing_keys=sorted(key for key in english_kinds if key not in locale_kinds),
				extra_keys=sorted(key for key in locale_kinds if key not in english_kinds),
				kind_mismatches=sorted(
					key for key in english_kinds
					if key in locale_kinds and english_kinds[key] != locale_kinds[key]
				),
				unsupported_paths=locale_file.unsupported_paths,
			)
			if file_report.missing_keys or file_report.extra_keys or file_report.kind_mismatches or file_report.unsupported_paths:
				report.files.append(file_report)

		for file_name in sorted(locale_files):
			matching_english_name = 'en.yaml' if file_name == f'{locale_dir.name}.yaml' else file_name
			if matching_english_name not in english_files:
				report.extra_files.append(file_name)

		if report.missing_files or report.extra_files or report.files:
			reports.append(report)

	return reports


def main() -> int:
	root_dir = Path.cwd()
	reports = audit_translations(root_dir)
	if not reports:
		print('[parity] OK: locale files match English key parity')
		return 0

	print('[parity] FAILED: locale drift detected')
	for report in reports:
		print(f'\n[{report.code}]')
		for file_name in report.missing_files:
			print(f'  missing file: {file_name}')
		for file_name in report.extra_files:
			print(f'  extra file: {file_name}')
		for file_report in report.files:
			print(f'  {file_report.path}')
			for key in file_report.missing_keys:
				print(f'    missing key: {key}')
			for key in file_report.extra_keys:
				print(f'    extra key: {key}')
			for key in file_report.kind_mismatches:
				print(f'    kind mismatch: {key}')
			for path in file_report.unsupported_paths:
				print(f'    unsupported structure: {path}')

	return 1


if __name__ == '__main__':
	raise SystemExit(main())