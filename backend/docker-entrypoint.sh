#!/bin/bash
set -e

# Install numpy compatible version if pandas is installed
python -c "import pandas" 2>/dev/null && pip install --no-cache-dir 'numpy<2.0.0' --quiet || true

# Start the application
exec "$@"
