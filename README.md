# Agentic AI Revenue Assistant

Privacy-first AI lead generation tool for Hong Kong telecom companies. Analyzes customer data while maintaining strict privacy controls and generates actionable sales recommendations.

## 🎯 Features

- **Privacy-First Design**: All sensitive data pseudonymized immediately upon upload
- **AI-Powered Analysis**: Uses DeepSeek LLM via OpenRouter for intelligent lead scoring
- **Three HK Branding**: Styled with Three HK color scheme and telecom-specific offers
- **Compliance Ready**: GDPR and Hong Kong PDPO compliant data handling
- **Interactive Dashboard**: Streamlit-based UI with real-time analysis results

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key (for DeepSeek LLM access)

### Installation

1. **Clone and setup the project:**
   ```bash
   cd "agentic-ai v1"
   ```

2. **Create virtual environment:**
   
   **Windows PowerShell:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   **Linux/macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and configuration
   ```

5. **Run the application:**
   ```bash
   streamlit run src/main.py
   ```

### Testing

**Quick App Check:**
```bash
python run_tests.py check
```

**Unit Tests:**
```bash
python run_tests.py unit
```

**End-to-End Tests (with Playwright):**
```bash
python run_tests.py e2e
```

**All Tests:**
```bash
python run_tests.py all
```

## 📂 Project Structure

```
agentic-ai v1/
├── src/
│   ├── components/          # Streamlit UI components
│   │   ├── home.py         # Home page
│   │   ├── layout.py       # Layout and styling
│   │   └── upload.py       # File upload (to be implemented)
│   ├── utils/              # Utility modules
│   │   └── logger.py       # Logging with privacy protection
│   └── main.py             # Main application entry point
├── config/
│   └── app_config.py       # Application configuration
├── data/
│   ├── raw/                # Raw uploaded data (encrypted)
│   └── processed/          # Processed anonymized data
├── tasks/                  # Task Master project management
├── documentation/          # Project documentation
├── requirements.txt        # Python dependencies
└── .env                    # Environment configuration
```

## 🔧 Configuration

Key environment variables in `.env`:

- `OPENROUTER_API_KEY`: Your OpenRouter API key for DeepSeek access
- `ENCRYPTION_KEY`: Encryption key for data protection (change from default!)
- `MAX_RECORDS`: Maximum customer records to process (default: 10,000)
- `PRIMARY_COLOR`: Three HK green color (#00FF00)

## 🔒 Privacy & Security

- **Immediate Pseudonymization**: All PII masked before processing
- **No Raw Data in AI**: Only anonymized data sent to LLM services
- **Encryption**: Data encrypted at rest and in transit
- **Audit Logging**: All data operations logged for compliance
- **Session Management**: Automatic data cleanup after sessions

## 📊 Sample Data

The project includes sample datasets:
- `sample-customer-data-20250714.csv`: Customer profiles and demographics
- `sample_purchase_history.csv`: Transaction and engagement data

## 🧪 Development

This project uses Task Master for development management:

```bash
# View current tasks
# (Task Master commands available through integrated tools)

# Current status: Task 1 (Project Setup) - In Progress
```

### Development Phases

1. **Foundation** (Tasks 1-5): Basic setup, UI, privacy layer
2. **Core AI** (Tasks 6-10): Data processing, LLM integration, analysis
3. **User Experience** (Tasks 11-13): Dashboard, features, export
4. **Production** (Tasks 14-15): Security, compliance, optimization

## 🤝 Contributing

1. Follow the Task Master development workflow
2. Ensure all privacy requirements are maintained
3. Test with sample data before using real customer information
4. Update documentation for any new features

## 📄 License

This project is designed for telecom industry demonstration purposes.

## 🆘 Support

For issues or questions:
1. Check the Task Master project management system
2. Review the privacy and security documentation
3. Ensure all environment variables are properly configured

---

**Built with privacy-first principles for Hong Kong telecom companies** 🇭🇰 