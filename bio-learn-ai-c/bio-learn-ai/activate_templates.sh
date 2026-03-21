#!/bin/bash
# BioLearn AI - Quick Activation Script
# This script activates all new template files

echo "🚀 BioLearn AI - Activating New Templates..."
echo ""

# Navigate to templates directory
cd "$(dirname "$0")/templates"

# Backup old files
echo "📦 Backing up old files..."
[ -f welcome.html ] && mv welcome.html welcome_old.html && echo "  ✓ Backed up welcome.html"
[ -f login.html ] && mv login.html login_old.html && echo "  ✓ Backed up login.html"
[ -f signup.html ] && mv signup.html signup_old.html && echo "  ✓ Backed up signup.html"
[ -f index.html ] && mv index.html index_old.html && echo "  ✓ Backed up index.html"

echo ""
echo "🔄 Activating new templates..."

# Activate new files
[ -f welcome_new.html ] && mv welcome_new.html welcome.html && echo "  ✓ Activated new home page"
[ -f login_new.html ] && mv login_new.html login.html && echo "  ✓ Activated new login page"
[ -f signup_new.html ] && mv signup_new.html signup.html && echo "  ✓ Activated new signup page"
[ -f dashboard_new.html ] && mv dashboard_new.html index.html && echo "  ✓ Activated new dashboard"

echo ""
echo "✅ All templates activated successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Update database: python -c 'from app import app, db; app.app_context().push(); db.create_all()'"
echo "2. Add Google OAuth credentials to .env"
echo "3. Restart Flask: python app.py"
echo "4. Visit: http://127.0.0.1:5000"
echo ""
