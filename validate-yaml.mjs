import fs from 'node:fs/promises'
import path from 'node:path'
import YAML from 'yaml'

/**
 * Recursively find all .yaml/.yml files under a directory.
 *
 * This is intended for translators who want a quick local sanity check
 * before opening a PR.
 *
 * @param {string} rootDir Absolute path to start searching from.
 * @returns {Promise<string[]>} Absolute file paths.
 */
async function findYamlFiles(rootDir) {
	/** @type {string[]} */
	const results = []

	/**
	 * @param {string} dir
	 */
	async function walk(dir) {
		const entries = await fs.readdir(dir, { withFileTypes: true })
		for (const entry of entries) {
			const fullPath = path.join(dir, entry.name)
			if (entry.isDirectory()) {
				if (entry.name === 'node_modules') continue
				if (entry.name.startsWith('.')) continue
				await walk(fullPath)
				continue
			}

			if (!entry.isFile()) continue
			const lower = entry.name.toLowerCase()
			if (lower.endsWith('.yaml') || lower.endsWith('.yml')) {
				results.push(fullPath)
			}
		}
	}

	await walk(rootDir)
	return results
}

/**
 * Validate a YAML file by attempting to parse it.
 *
 * @param {string} filePath Absolute file path.
 * @returns {Promise<{ ok: true } | { ok: false, error: Error }>} Parse result.
 */
async function validateYamlFile(filePath) {
	try {
		const text = await fs.readFile(filePath, 'utf8')
		YAML.parse(text)
		return { ok: true }
	} catch (error) {
		return { ok: false, error: /** @type {Error} */ (error) }
	}
}

async function main() {
	const rootDir = process.cwd()
	const yamlFiles = await findYamlFiles(rootDir)
	yamlFiles.sort((a, b) => a.localeCompare(b))

	/** @type {Array<{ file: string, error: Error }>} */
	const failures = []

	for (const file of yamlFiles) {
		const result = await validateYamlFile(file)
		if (!result.ok) {
			failures.push({ file, error: result.error })
		}
	}

	if (failures.length === 0) {
		console.log(`[yaml] OK: ${yamlFiles.length} files`)
		return
	}

	console.error(`[yaml] FAILED: ${failures.length}/${yamlFiles.length} files`)
	for (const { file, error } of failures) {
		const relative = path.relative(rootDir, file).replace(/\\/g, '/')
		console.error(`\n- ${relative}`)
		console.error(String(error.message || error))
	}

	process.exitCode = 1
}

main().catch(error => {
	console.error('[yaml] Validator crashed')
	console.error(error)
	process.exit(1)
})
