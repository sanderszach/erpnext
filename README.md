# ERPNext Project

A Docker-based local development environment for ERPNext + Frappe with live code editing.

## Structure

```
erpnext-project/
├── docker-compose.dev.yml   # Docker services configuration
├── apps/
│   ├── erpnext/             # ERPNext source code (bind-mounted)
│   └── agent/               # Custom Python app (standalone)
└── frappe-bench/            # Runtime only (auto-generated, gitignored)
```

## Prerequisites

- **Docker Desktop** (with Docker Compose v2)
- **Git**
- macOS or Linux host

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url> erpnext-project
cd erpnext-project
```

### 2. Start Docker Services

```bash
docker compose -f docker-compose.dev.yml up -d
```

### 3. Initialize the Bench (first time only)

```bash
# Enter the container
docker compose -f docker-compose.dev.yml exec bench bash

# Inside the container - initialize bench
cd /home/frappe
bench init temp-bench --frappe-branch v16.0.0-beta.1 --skip-redis-config-generation --python python3.14

# Move runtime files to the mounted directory
cd /home/frappe
cp -r temp-bench/config frappe-bench/
cp -r temp-bench/env frappe-bench/
cp -r temp-bench/logs frappe-bench/
cp -r temp-bench/sites frappe-bench/
cp -r temp-bench/Procfile frappe-bench/
cp -r temp-bench/apps/frappe frappe-bench/apps/
rm -rf temp-bench

# Recreate virtualenv (fix symlinks)
cd /home/frappe/frappe-bench
rm -rf env
uv venv env --seed --python python3.14

# Install apps
uv pip install -e apps/frappe --python env/bin/python
uv pip install -e apps/erpnext --python env/bin/python

# Install npm dependencies for ERPNext
cd apps/erpnext && yarn install && cd ../..

# Configure Redis
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379

# Create site (using localhost so you can access it directly)
bench new-site localhost --admin-password=admin --db-root-username=root --db-root-password=admin --db-host=db

# Add erpnext to apps.txt
echo -e 'frappe\nerpnext' > sites/apps.txt

# Install ERPNext on site
bench --site localhost install-app erpnext

# Build assets
bench build

# Exit container
exit
```

### 4. Start Development Server

```bash
docker compose -f docker-compose.dev.yml exec bench bash -c "cd /home/frappe/frappe-bench && bench start"
```

### 5. Access ERPNext

- **URL:** http://localhost:8000
- **Username:** `Administrator`
- **Password:** `admin`

## Daily Development Workflow

### Start the environment

```bash
# Terminal 1: Start Docker services
docker compose -f docker-compose.dev.yml up -d

# Terminal 2: Start bench
docker compose -f docker-compose.dev.yml exec bench bash
cd /home/frappe/frappe-bench
bench start
```

### Stop the environment

```bash
docker compose -f docker-compose.dev.yml down
```

### Reset everything (nuclear option)

```bash
docker compose -f docker-compose.dev.yml down -v
docker run --rm -v $(pwd):/workspace alpine sh -c "rm -rf /workspace/frappe-bench"
# Then follow Quick Start from step 2
```

## Live Code Editing

- **Python changes**: Auto-reload (Werkzeug dev server watches for changes)
- **JavaScript/CSS changes**: Run `bench build` or `bench build --watch`
- Code in `apps/erpnext/` is bind-mounted, so edits on host appear instantly in container

## Key Commands (inside container)

```bash
# Rebuild frontend assets
bench build

# Watch for frontend changes
bench build --watch

# Run migrations
bench --site localhost migrate

# Clear cache
bench --site localhost clear-cache

# Open console
bench --site localhost console

# Create a new custom app
bench new-app my_custom_app
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Web | 8000 | ERPNext web interface |
| SocketIO | 9000 | Real-time updates |
| MariaDB | 3306 | Database |
| Redis Cache | 6379 | Cache |
| Redis Queue | 6379 | Background jobs |

## Troubleshooting

### Assets not loading (404 errors)

```bash
docker compose -f docker-compose.dev.yml exec bench bash -c "cd /home/frappe/frappe-bench && bench build"
```

### Database connection issues

```bash
# Check if MariaDB is running
docker compose -f docker-compose.dev.yml logs db
```

### Permission errors in frappe-bench

```bash
# Fix permissions from host
docker run --rm -v $(pwd):/workspace alpine sh -c "chown -R 1000:1000 /workspace/frappe-bench"
```

## Architecture Notes

- `apps/erpnext/` - Treat as upstream source; avoid direct modifications
- `apps/agent/` - Standalone Python/FastAPI app (not a Frappe app)
- `frappe-bench/` - Runtime only; fully regenerated during setup
- For customizations, create a proper Frappe custom app using `bench new-app`

## License

See individual app licenses.
