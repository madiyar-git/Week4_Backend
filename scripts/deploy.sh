#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
ENVIRONMENT=""

usage() {
    echo "Usage: $0 <staging|production> [--dry-run]"
    exit 1
}

if [ $# -lt 1 ]; then
    echo " Error: Missing required environment argument."
    usage
fi

ENVIRONMENT="$1"
shift

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo " Error: Invalid environment '$ENVIRONMENT'. Must be 'staging' or 'production'."
    usage
fi

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo " Error: Unknown option '$1'"
            usage
            ;;
    esac
done

echo "🚀 Starting deployment to environment: [$ENVIRONMENT]"
if [ "$DRY_RUN" = true ]; then
    echo "ℹ  RUNNING IN DRY-RUN MODE (No real infrastructure changes will be executed)"
fi
echo "--------------------------------------------------------"

execute_step() {
    local step_name="$1"
    local command="$2"

    echo "▶️ [$step_name]..."
    if [ "$DRY_RUN" = true ]; then
        echo "   [DRY-RUN] Would execute: $command"
    else
        eval "$command"
    fi
    echo " [$step_name] completed."
    echo ""
}

execute_step "1. Fetching latest codebase" "git pull origin main"
execute_step "2. Pulling / Building Docker Images" "docker compose build --no-cache"
execute_step "3. Applying Database Migrations" "docker compose exec -T web python manage.py migrate"
execute_step "4. Collecting Static Files" "docker compose exec -T web python manage.py collectstatic --noinput"
execute_step "5. Restarting Application Services" "docker compose restart web"

echo "▶ [6. Running Service Healthcheck]..."
if [ "$DRY_RUN" = true ]; then
    echo "   [DRY-RUN] Would execute: curl -f http://localhost:8000/api/health/"
else
    if curl -s -f http://localhost:8000/ > /dev/null; then
        echo " Service Healthcheck passed!"
    else
        echo " Healthcheck failed! Rolling back or alerting required."
        exit 1
    fi
fi

echo "--------------------------------------------------------"
echo "🎉 Deployment to [$ENVIRONMENT] finished successfully!"