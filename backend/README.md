# Discovery Project

A LangGraph-based application with integrated MCP (Model Context Protocol) support.

## Quick Start

### 1. Activate the Virtual Environment

```bash
cd /Users/kannan/DPAS/discovery
source venv/bin/activate
```

### 2. Verify Installation

```bash
pip check
```

You should see: `No broken requirements found.`

### 3. Run LangGraph

```bash
langgraph dev
```

Or use the LangGraph CLI commands:

```bash
langgraph --help
```

### 4. Deactivate When Done

```bash
deactivate
```

## Project Structure

```
discovery/
├── agent-chat-ui/         # Next.js frontend
│   ├── src/
│   ├── package.json
│   └── ...
├── venv/                  # Python virtual environment
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── DEPENDENCY_RESOLUTION.md  # Dependency fix documentation
```

## Dependencies

### Python Backend
- **FastAPI** - Web framework
- **LangGraph** - Orchestration framework
- **MCP** - Model Context Protocol
- **OpenTelemetry** - Observability
- **httpx** - HTTP client

### Frontend
- **Next.js** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

## Development

### Backend (Python)

Always activate the virtual environment first:
```bash
source venv/bin/activate
```

Install additional packages:
```bash
pip install package-name
pip freeze > requirements.txt  # Update requirements
```

### Frontend (Next.js)

Navigate to the frontend directory:
```bash
cd agent-chat-ui
pnpm install
pnpm dev
```

## Dependency Management

All Python dependency conflicts have been resolved. See `DEPENDENCY_RESOLUTION.md` for details.

**Key Points:**
- ✅ All packages use compatible versions
- ✅ No dependency conflicts
- ✅ Clean virtual environment
- ✅ Isolated from global Python installation

## Troubleshooting

### SSL Certificate Errors

If you encounter SSL certificate errors with pip:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org package-name
```

### Virtual Environment Not Found

Recreate it:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Errors

Make sure you're using the virtual environment, not the global Python installation.

## Documentation

- `DEPENDENCY_RESOLUTION.md` - How dependency conflicts were resolved
- `requirements.txt` - Python package specifications
- `agent-chat-ui/README.md` - Frontend documentation

## Contributing

1. Always use the virtual environment
2. Keep dependencies minimal
3. Document any new dependencies
4. Test before committing

## License

See LICENSE file in agent-chat-ui directory.

