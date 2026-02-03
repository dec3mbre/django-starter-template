#!/bin/bash
# Usage: ./scripts/startapp.sh app_name
# Creates a new Django app in src/apps/

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/startapp.sh <app_name>"
    echo "Example: ./scripts/startapp.sh blog"
    exit 1
fi

APP_NAME=$1
APP_PATH="src/apps/$APP_NAME"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

if [ -d "$APP_PATH" ]; then
    echo "Error: App '$APP_NAME' already exists at $APP_PATH"
    exit 1
fi

echo "Creating app '$APP_NAME' in $APP_PATH..."
python manage.py startapp "$APP_NAME" "$APP_PATH"

# Fix apps.py to use correct path
sed -i '' "s/name = \"$APP_NAME\"/name = \"apps.$APP_NAME\"/" "$APP_PATH/apps.py"

echo "✅ App '$APP_NAME' created successfully!"