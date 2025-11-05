# LedgerTrace 🔍

**AI-Powered Entity Risk Analysis for Financial Transparency**

LedgerTrace combines business registration data with property records to identify potential red flags in organizational entities. Built for journalists, investigators, and transparency advocates.

![LedgerTrace Demo](https://img.shields.io/badge/Demo-Live-green) ![Docker](https://img.shields.io/badge/Docker-Ready-blue) ![License](https://img.shields.io/badge/License-MIT-yellow) ![Security](https://img.shields.io/badge/Security-Hardened-red) ![Version](https://img.shields.io/badge/Version-1.0.0-blue)

🌟 **[Live Demo](https://ledgertrace.vercel.app)** • 📚 **[Documentation](https://github.com/Adahandles/ledgertrace/wiki)** • 🐛 **[Report Issues](https://github.com/Adahandles/ledgertrace/issues)** • 💬 **[Discussions](https://github.com/Adahandles/ledgertrace/discussions)**

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

### One-Command Deploy
```bash
git clone https://github.com/Adahandles/ledgertrace.git
cd ledgertrace
docker-compose up --build
```

**Access the app:**
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000  
- **API Documentation:** http://localhost:8000/api/docs

**🌍 Live Production Demo:** [https://ledgertrace.vercel.app](https://ledgertrace.vercel.app)

## 🎯 What LedgerTrace Does

### Risk Analysis Features
- **Entity Verification** - Cross-references business registration data
- **Property Analysis** - Integrates Florida county property records  
- **Red Flag Detection** - Identifies suspicious patterns automatically
- **Source Verification** - Direct links to government databases

### Risk Indicators
- ⚠️ Missing EIN or business registration
- 🏠 Delinquent property taxes
- 📮 PO Box addresses (potential mail drops)
- 🏗️ Vacant or undeveloped properties
- 👥 Complex officer structures
- 💰 Unreported market values

## 📊 Example Analysis

**Input:** 
```json
{
  "name": "Sample Foundation",
  "address": "PO Box 456, Ocala, FL"
}
```

**Output:**
```json
{
  "name": "Sample Foundation",
  "risk_score": 90,
  "anomalies": [
    "⚠️ No EIN provided.",
    "⚠️ PO Box detected in address.",
    "⚠️ Delinquent property taxes detected.",
    "⚠️ Property address may be a mail drop service."
  ],
  "property": {
    "county": "Marion",
    "owner_name": "Property Owner LLC",
    "land_use": "Mail Drop Service",
    "market_value": "N/A",
    "delinquent_taxes": true,
    "source_url": "https://www.pa.marion.fl.us/"
  }
}
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SvelteKit     │    │   FastAPI       │    │  Florida County │
│   Frontend      │◄──►│   Backend       │◄──►│  Property APIs  │
│   (Port 5173)   │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Sunbiz API    │
                       │   IRS Lookup    │
                       │   SBA Records   │
                       └─────────────────┘
```

## 🔧 Development Setup

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development  
```bash
cd frontend
npm install
npm run dev -- --host --port 5173
```

### Full Stack with Docker
```bash
docker-compose up --build
```

## 📡 API Documentation

### Analyze Entity
**POST** `/analyze`

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Entity Name",
    "address": "123 Main St, City, FL", 
    "ein": "12-3456789",
    "officers": ["John Doe", "Jane Smith"]
  }'
```

### Health Check
**GET** `/`
```bash
curl http://localhost:8000/
# Returns: {"status": "LedgerTrace API is live"}
```

## 🎨 Frontend Features

- **Real-time Risk Scoring** - Color-coded risk levels (Green/Yellow/Red)
- **Property Integration** - County records with tax status
- **Source Links** - Direct links to government databases
- **Responsive Design** - Works on desktop and mobile
- **Demo Mode** - Pre-loaded examples for testing

## 📁 Project Structure

```
ledgertrace/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── analyzer.py          # Risk analysis logic
│   │   ├── models.py            # Pydantic data models
│   │   └── property_scraper.py  # County property integration
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── routes/
│   │       └── +page.svelte     # Main application UI
│   ├── Dockerfile
│   ├── package.json
│   └── svelte.config.js
├── data_ingestion/
│   ├── entity_resolver.py       # Business entity lookup
│   └── sunbiz_fetcher.py       # Florida Sunbiz integration
├── docker-compose.yml
└── README.md
```

## 🌟 Use Cases

### 📰 Journalism
- **Grant Fraud Investigation** - Verify nonprofit legitimacy
- **Political Donor Analysis** - Cross-reference business interests
- **Real Estate Corruption** - Track property ownership patterns

### 🏛️ Government Transparency
- **Vendor Due Diligence** - Pre-qualify contractors
- **Grant Application Review** - Automated red flag detection  
- **Public Records Integration** - Streamline transparency requests

### 💼 Private Sector
- **Client Onboarding** - Enhanced KYC processes
- **Partnership Due Diligence** - Risk assessment automation
- **Compliance Monitoring** - Ongoing entity verification

## 🚧 Current Limitations

- **Florida-Focused** - Property data limited to Florida counties
- **Mock Data** - Demo uses simulated property records  
- **Rate Limiting** - No API throttling implemented yet
- **Authentication** - Public access (no user accounts)

## 🛣️ Roadmap

### Phase 1 (Current)
- ✅ Entity risk scoring
- ✅ Property integration
- ✅ Web interface
- ✅ Docker deployment

### Phase 2 (Next)
- 🔄 Real county scraper integration
- 🔄 PostgreSQL database
- 🔄 User authentication
- 🔄 Batch CSV analysis

### Phase 3 (Future)  
- 🔄 Multi-state property data
- 🔄 API rate limiting
- 🔄 Export/reporting features
- 🔄 Mobile app

## 🤝 Contributing

We welcome contributions! Areas where help is needed:

1. **County Scrapers** - Add more Florida counties
2. **Data Sources** - Integrate additional public records
3. **UI/UX** - Improve the frontend experience  
4. **Documentation** - Expand setup and usage guides
5. **Testing** - Add automated test coverage

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Adahandles/ledgertrace/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Adahandles/ledgertrace/discussions)
- **Documentation:** [Wiki](https://github.com/Adahandles/ledgertrace/wiki)

## ⚖️ Legal Disclaimer

LedgerTrace aggregates publicly available information for transparency and due diligence purposes. All data is sourced from government databases and public records. This tool:

- **Is not financial or legal advice**
- **Should not be the sole basis for decisions**
- **May contain errors or outdated information**
- **Is provided "as is" without warranties**

Users are responsible for verifying information through official sources before taking action.

---

**Built with ❤️ for transparency and accountability**

*LedgerTrace - Making public data accessible and actionable*
