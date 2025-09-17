# 🎉 Pollcast: Your Opinion Superpower! 🌟

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frappe](https://img.shields.io/badge/Frappe-Framework-blue)](https://frappeframework.com)

A powerful, feature-rich polling and surveying application built on the Frappe framework. Collect opinions, analyze trends, and make data-driven decisions with real-time analytics and PWA capabilities!

## ✨ Features

- 📊 **Interactive Polls**: Single/multiple choice questions with live results
- 📝 **Advanced Surveys**: Multi-page questionnaires with various question types
- 📈 **Real-time Analytics**: Live dashboards with charts and insights
- 📱 **PWA Ready**: Offline support, push notifications, mobile installation
- 🤖 **Smart Automation**: Auto-close polls, scheduled reports, data cleanup
- 🔄 **Live Updates**: Server-Sent Events for instant response notifications
- 🎨 **Beautiful UI**: Modern design with smooth animations
- 📧 **Email Integration**: Automated reports and notifications

## 🚀 Quick Start

1. **Install Frappe Bench**

   ```bash
   pip install frappe-bench
   bench init frappe-bench
   cd frappe-bench
   ```

2. **Get Pollcast**

   ```bash
   bench get-app https://github.com/your-org/pollcast.git
   bench install-app pollcast
   ```

3. **Start Server**

   ```bash
   bench start
   ```

4. **Create Your First Poll!**
   - Visit your Frappe site
   - Go to Pollcast > Poll > New Poll
   - Fill in details and share!

## 📖 Documentation

- **[Complete User Guide](USER_GUIDE.md)** - Everything you need to know
- **API Documentation** - Coming soon
- **Developer Guide** - Contribution guidelines

## 🎯 Use Cases

- **Event Planning**: Gather preferences for themes, dates, venues
- **Market Research**: Collect customer feedback and preferences
- **Team Decisions**: Quick polls for project choices
- **Education**: Student feedback and course evaluations
- **Community Engagement**: Town hall meetings and civic participation

## 🏗️ Architecture

Built with modern web technologies:

- **Frontend**: Vue.js 3, Tailwind CSS, Chart.js
- **Backend**: Python + Frappe Framework
- **Database**: MariaDB/MySQL
- **Real-time**: Server-Sent Events (SSE)
- **PWA**: Service Workers, IndexedDB
- **Caching**: Multiple strategies for optimal performance

## 🤝 Contributing

We love contributions! Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to collect some amazing opinions? Let's poll! 📊✨**
