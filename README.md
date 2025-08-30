# PILOT 🚀
**Product Innovation & Lifecycle Orchestration Tool**

PILOT is a streamlined web application that helps product teams transform simple use case descriptions into comprehensive product documentation, including functional requirements, architecture diagrams, and system design documents.

![PILOT Interface](https://img.shields.io/badge/Built%20with-Streamlit-FF6B6B)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **📝 Use Case Management**: Create and manage product use cases with intuitive descriptions
- **🤖 AI-Powered Generation**: Automatically generate product artifacts using Claude AI
- **📊 Architecture Diagrams**: Create Mermaid.js diagrams for system architecture
- **📋 Requirements Documentation**: Generate functional and non-functional requirements
- **🏗️ System Design**: Produce comprehensive system design documents
- **📖 Interactive Documentation**: Built-in MkDocs server for viewing generated documentation
- **🎯 User-Friendly Interface**: Clean, tab-based interface for easy navigation

## 🏗️ Architecture

```
product-planner/
├── frontend/           # Streamlit web application
│   ├── main.py        # Main application file
│   └── commands.md    # AI command configurations
├── workspace/         # Generated use cases and artifacts
│   └── [use-case]/    # Individual use case directories
│       ├── usecase.md # Use case description
│       ├── ra-fr.md   # Functional requirements
│       ├── ra-nfr.md  # Non-functional requirements
│       ├── ra-diagrams.md # Architecture diagrams
│       ├── ra-sdd.md  # System design document
│       └── _ra/       # Generated documentation site
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Claude AI CLI configured with API access
- Streamlit
- MkDocs (installed automatically)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/cloudtriquetra/product-planner.git
   cd product-planner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Claude AI CLI**
   ```bash
   # Follow Claude AI CLI setup instructions
   # Ensure you have API access configured
   ```

4. **Run the application**
   ```bash
   cd frontend
   streamlit run main.py
   ```

5. **Access PILOT**
   Open your browser to `http://localhost:8501`

## 📖 Usage Guide

### 1. Creating a Use Case

1. Navigate to the **Product Use Case** tab
2. Expand "Create a new Use Case"
3. Enter a descriptive name and detailed description
4. Click "Save Use Case"

**Example Use Case:**
```
Name: Simple Calculator
Description: I need to build a web-based calculator that works on all devices. 
It should handle basic math operations like addition, subtraction, multiplication, 
and division. Users should be able to enter numbers either by clicking buttons 
or using their keyboard...
```

### 2. Generating Product Artifacts

1. Select your use case from the dropdown
2. Switch to the **Product Planning** tab
3. Choose an artifact type:
   - **Functional Requirements**: Core feature specifications
   - **Non-Functional Requirements**: Performance, security, usability requirements
   - **Architecture Diagrams**: Visual system architecture with Mermaid.js
   - **System Design Document**: Comprehensive technical design
4. Click "Generate Product Artifacts"
5. Wait for AI processing to complete

### 3. Viewing Results

1. Navigate to the **Results** tab
2. Select a report to view from the dropdown
3. Review generated content with rendered diagrams
4. Use the documentation server link for a polished view

### 4. Documentation Server

Generated artifacts automatically create an MkDocs documentation site:
- Accessible via the "View Documentation" button
- Professional formatting with Material theme
- Interactive Mermaid.js diagrams
- Searchable content

## 🛠️ Configuration

### Command Templates (`frontend/commands.md`)

Customize AI generation commands by editing the commands configuration:

```markdown
1. Functional Requirement,claude -p "/ra-fr $USECASE" --dangerously-skip-permissions,ra-fr.md
2. Non-Functional Requirement,claude -p "/ra-nfr $USECASE" --dangerously-skip-permissions,ra-nfr.md
3. Architecture Diagrams,claude -p "/ra-diagrams $USECASE" --dangerously-skip-permissions,ra-diagrams.md
4. System Design Document,claude -p "/ra-sdd $USECASE" --dangerously-skip-permissions,ra-sdd.md
```

Format: `Name,Command Template,Output File`

### Streamlit Configuration

The application uses centered layout with custom branding:
- Custom logo/favicon support
- Responsive design
- Session state management for multi-user scenarios

## 🔧 Advanced Features

### Port Management
- Automatic port allocation for documentation servers
- Process management for background MkDocs servers
- Graceful server shutdown and restart

### Error Handling
- Comprehensive error messages for failed generations
- Validation for missing dependencies
- Process monitoring and recovery

### Session Management
- Persistent use case selection across tabs
- Background process tracking
- Status indicators for running operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

### Python Dependencies
```
streamlit>=1.28.0
streamlit-mermaid>=0.1.0
streamlit-shadcn-ui>=0.1.0
```

### Documentation Dependencies (Auto-installed)
```
mkdocs>=1.5.0
mkdocs-material>=9.0.0
mkdocs-mermaid2-plugin>=1.0.0
pymdown-extensions>=10.0.0
mkdocs-awesome-pages-plugin>=2.8.0
mkdocs-minify-plugin>=0.7.0
mkdocs-git-revision-date-localized-plugin>=1.2.0
```

### External Dependencies
- Claude AI CLI with valid API access
- Git (for repository management)

## 🐛 Troubleshooting

### Common Issues

**1. Claude AI CLI not found**
```bash
# Install and configure Claude AI CLI
# Ensure it's in your PATH
```

**2. Port conflicts**
- PILOT automatically manages ports starting from 8005
- Kill conflicting processes if needed: `lsof -ti:PORT | xargs kill`

**3. Documentation generation fails**
- Check Claude AI API limits and permissions
- Verify use case description is detailed enough
- Review error logs in the application

**4. MkDocs dependencies**
- Dependencies are auto-installed per session
- Manual installation: `pip install mkdocs mkdocs-material`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Powered by [Claude AI](https://claude.ai/) for intelligent content generation
- Documentation generated with [MkDocs](https://www.mkdocs.org/) and Material theme
- Diagrams rendered with [Mermaid.js](https://mermaid.js.org/)

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the [Wiki](../../wiki) for detailed documentation
- Review existing discussions and solutions

---

**Made with ❤️ for product teams who want to move fast and build great things**
