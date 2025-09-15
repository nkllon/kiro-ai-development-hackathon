# Makefile System Best Practices

## General Guidelines

1. **Use descriptive target names** - Make target names self-documenting
2. **Include help text** - Add descriptions using `##` comments
3. **Organize by category** - Group related targets together
4. **Use PHONY for non-file targets** - Mark targets that don't create files
5. **Keep dependencies minimal** - Only include necessary dependencies

## Target Naming Conventions

- Use lowercase with hyphens: `build-python`
- Use descriptive verbs: `validate`, `deploy`, `clean`
- Use category prefixes: `test-unit`, `test-integration`

## Variable Usage

- Use uppercase for global variables: `VERSION`
- Use descriptive names: `PYTHON_VERSION` not `PV`
- Group related variables together
