# ERPNext Project Monorepo

This is a monorepo containing ERPNext and related applications and libraries.

## Structure

```
erpnext-project/
├── apps/
│   └── erpnext/          # ERPNext application (fork)
├── libs/                  # Shared libraries (to be added)
└── package.json          # Root package configuration
```

## Getting Started
### Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Python >= 3.10 (for ERPNext)

### Installation

Install dependencies for all workspaces:

```bash
pnpm install
```

### Working with ERPNext

The ERPNext app is located in `apps/erpnext/`. Refer to the [ERPNext README](./apps/erpnext/README.md) for setup instructions.

### Adding New Apps

To add a new app:

1. Create a new directory in `apps/`
2. Add a `package.json` file to the new app
3. Run `pnpm install` from the root to link the workspace

### Adding New Libraries

To add a new shared library:

1. Create a new directory in `libs/`
2. Add a `package.json` file to the new library
3. Run `pnpm install` from the root to link the workspace

## Scripts

- `pnpm install:all` - Install dependencies for all workspaces
- `pnpm build` - Build all workspaces
- `pnpm test` - Run tests for all workspaces
- `pnpm lint` - Lint all workspaces

## License

See individual workspace licenses.

