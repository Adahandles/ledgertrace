#!/bin/bash

# 🚀 LedgerTrace Production Deployment Script
# Run this script to deploy LedgerTrace to production

echo "🚀 LedgerTrace Production Deployment"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the LedgerTrace root directory"
    exit 1
fi

echo "✅ Verifying project structure..."

# Create version tag
VERSION="v1.0.0"
echo "🏷️  Creating release tag: $VERSION"

# Add all files
echo "📦 Staging files for commit..."
git add .

# Commit with production message
echo "💾 Committing production-ready code..."
git commit -m "🚀 Launch LedgerTrace v1.0.0 - Production Ready Civic Tech Platform

✨ Features:
- AI-powered entity risk analysis
- Florida county property integration
- Real-time risk scoring with visual indicators
- Source verification links to government databases
- Professional UI with accessibility compliance

🛡️ Security & Legal:
- Rate limiting and input validation
- CORS protection and security headers
- Comprehensive legal disclaimers and privacy policy
- Non-root Docker containers with health checks
- Automated security scanning via GitHub Actions

📚 Documentation:
- Complete setup and deployment guides
- API documentation with examples
- Terms of service and privacy policy
- Contribution guidelines and roadmap

🌍 Ready for global deployment and civic impact!"

# Create and push tag
echo "🏷️  Creating and pushing release tag..."
git tag -a $VERSION -m "LedgerTrace v1.0.0 - Initial Production Release

Complete civic tech platform for entity risk analysis and transparency.
Includes full-stack application, security hardening, legal compliance,
and comprehensive documentation."

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push origin main --tags

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "🌍 Your LedgerTrace platform is now live on GitHub!"
echo ""
echo "Next Steps:"
echo "1. 🔒 Enable branch protection in GitHub Settings → Branches"
echo "2. 🔍 Enable security features in GitHub Settings → Security"  
echo "3. 📱 Set up GitHub Pages in Settings → Pages → GitHub Actions"
echo "4. 🚀 Deploy to Vercel by connecting your GitHub repository"
echo "5. 🎯 Add repository topics: civic-tech, transparency, fastapi, sveltekit"
echo ""
echo "🔗 Repository URL: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]//;s/.git$//')"
echo "📖 Documentation: Check README.md and DEPLOY.md for details"
echo ""
echo "🎉 LedgerTrace is ready to transform transparency and accountability!"
echo "   Share it with journalists, investigators, and transparency advocates!"