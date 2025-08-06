# Command-Line Interface (`simorc`)

```{toctree}
:maxdepth: 2

commands
usage-examples
```

**Implementation Status**: ✅ **COMPLETE** - Professional CLI with all core commands implemented

The entire workflow is managed through the `simorc` command-line tool with subcommands that map directly to architectural stages. The interface is built with Click for professional user experience.

**Current Dependencies**: `click`, `pydantic`, `pyyaml`, `pytest`, `jinja2`

## Quick Reference

| Command | Purpose | Status |
|---------|---------|--------|
| `simorc init` | Create new simulation project | ✅ Complete |
| `simorc validate` | Validate configuration files | ✅ Complete |
| `simorc build` | Generate sweep test cases | ✅ Complete |
| `simorc run` | Execute simulations | ✅ Complete |
| `simorc analyze` | Process results | 🚧 Planned |
| `simorc status` | View sweep progress | 📋 Placeholder |
| `simorc clean` | Clean up results | 📋 Placeholder |