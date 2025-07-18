# GutIntel

A comprehensive API for gut health intelligence, providing evidence-based information about ingredients, microbiome effects, and health outcomes.

## Overview

GutIntel is a FastAPI-based application that aggregates and analyzes scientific data about gut health ingredients and their effects on the microbiome. It provides structured data about probiotics, prebiotics, postbiotics, and other gut health supplements, including their microbiome effects, clinical evidence, and safety profiles.

## Features

- **Ingredient Database**: Comprehensive database of gut health ingredients with categorization and scoring
- **Microbiome Effects**: Detailed tracking of how ingredients affect different bacterial strains
- **Clinical Evidence**: Integration of scientific studies and research data
- **Health Outcomes**: Mapping of ingredients to specific health benefits
- **Interaction Analysis**: Understanding of ingredient interactions and combinations
- **Safety Information**: Comprehensive safety profiles and contraindications
- **RESTful API**: Clean, well-documented API endpoints for integration

## Technology Stack

- **Backend**: FastAPI with Python 3.8+
- **Database**: PostgreSQL with asyncpg driver
- **Configuration**: Pydantic settings with environment variable support
- **Validation**: Comprehensive data validation with Pydantic models
- **Documentation**: Auto-generated API documentation with Swagger/OpenAPI

## Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gutintel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the environment:
```bash
python setup.py
```

4. Configure your environment variables by editing the `.env` file:
```bash
# Database configuration
DATABASE_URL=postgresql://username:password@localhost:5432/gutintel

# API configuration
API_HOST=127.0.0.1
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# External APIs (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

5. Initialize the database:
```bash
psql -d gutintel -f schema.sql
```

6. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Project Structure

```
gutintel/
├── config.py              # Application configuration
├── setup.py               # Development environment setup
├── schema.sql             # Database schema
├── requirements.txt       # Python dependencies
├── models/                # Pydantic data models
│   ├── ingredient.py      # Ingredient-related models
│   ├── api.py            # API request/response models
│   └── validators.py      # Custom validators
├── database/              # Database layer
│   ├── connection.py      # Database connection management
│   ├── repositories.py    # Data access layer
│   └── seed_data.py       # Initial data seeding
├── tools/                 # Development tools
│   ├── data_importer.py   # Data import utilities
│   └── template_generator.py # Template generation
├── templates/             # Data templates
├── ingredients/           # Ingredient data files
├── logs/                  # Application logs
├── uploads/               # File uploads
└── static/                # Static files
```

## Data Models

### Ingredients
- Comprehensive ingredient profiles with categories (probiotic, prebiotic, etc.)
- Gut health scores and confidence ratings
- Dosage information and safety notes
- Alternative names and aliases

### Microbiome Effects
- Bacterial strain-specific effects
- Effect strength and confidence levels
- Mechanisms of action
- Scientific evidence backing

### Health Outcomes
- Specific health benefits and conditions
- Evidence quality and study types
- Population-specific effects
- Contraindications and warnings

### Clinical Studies
- Study metadata and quality assessment
- Result summaries and statistical significance
- Participant demographics and protocols
- Peer review and publication information

## API Endpoints

The API provides comprehensive endpoints for:

- `/ingredients/` - Ingredient management and retrieval
- `/microbiome/` - Microbiome effect data
- `/health-outcomes/` - Health benefit information
- `/studies/` - Clinical study data
- `/interactions/` - Ingredient interactions
- `/search/` - Advanced search capabilities

Full API documentation is available at `/docs` when running the application.

## 🔬 Scoring Methodology

GutIntel uses an evidence-weighted scoring system based on systematic scientific literature review, providing the industry's most rigorous and transparent gut health ingredient assessment. This methodology ensures healthcare-grade accuracy while maintaining commercial applicability.

### 📊 Gut Score Logic (0-10 Scale)

Our proprietary scoring system evaluates ingredients across multiple evidence dimensions:

| Score Range | Evidence Level | Criteria |
|-------------|----------------|----------|
| **9.0-9.5** | 🟢 Exceptional Evidence | Multiple high-quality RCTs, meta-analyses, dose-response established |
| **8.0-8.9** | 🟢 Strong Evidence | Several good RCTs, consistent results, clear beneficial effects |
| **7.0-7.9** | 🟡 Good Evidence | Some RCTs, generally positive results, reasonable mechanistic rationale |
| **6.0-6.9** | 🟡 Moderate Evidence | Limited clinical trials, mixed results, preliminary research |
| **5.0-5.9** | 🟠 Limited Evidence | Few human studies, mostly theoretical benefits |
| **3.0-4.9** | 🔴 Poor Evidence | Very limited research, safety concerns, conflicting results |

### ⭐ Confidence Score Logic (0-1.0 Scale)

Research quality assessment based on study design and reproducibility:

- **0.9-1.0 (Very High)**: Multiple meta-analyses, consistent results, large samples
- **0.7-0.8 (High)**: Several well-designed studies, generally consistent findings
- **0.5-0.6 (Moderate)**: Some good studies but limited scope, mixed results
- **0.3-0.4 (Low)**: Very limited research, high bias risk, conflicting results

### 🎯 Scoring Factors & Weights

Our algorithm considers five key dimensions:

1. **Study Design Quality (40%)**: RCTs > Observational > Case studies
2. **Sample Size & Duration (20%)**: Larger, longer studies score higher
3. **Consistency of Results (20%)**: Reproducible effects across studies
4. **Mechanistic Understanding (10%)**: Clear biological rationale
5. **Clinical Relevance (10%)**: Meaningful symptom improvements

### 🛡️ Conservative Approach

We deliberately use conservative scoring to ensure commercial accuracy and professional credibility. This approach:
- Protects against overpromising health benefits
- Builds trust with healthcare professionals
- Supports regulatory compliance
- Maintains scientific integrity

### 📋 Scoring Examples

```
LGG (Lactobacillus rhamnosus GG)
├── Gut Score: 9.5/10
├── Confidence: 0.95
└── Rationale: Most studied probiotic strain with 500+ publications

Inulin (Prebiotic Fiber)
├── Gut Score: 9.0/10  
├── Confidence: 0.95
└── Rationale: Extensive RCT evidence and multiple meta-analyses

Curcumin (Turmeric Extract)
├── Gut Score: 8.5/10
├── Confidence: 0.85
└── Rationale: Strong evidence but bioavailability concerns

Activated Charcoal
├── Gut Score: 3.0/10
├── Confidence: 0.40
└── Rationale: Safety concerns and limited clinical evidence
```

### 🔍 Quality Assurance

Our scoring methodology maintains the highest standards through:

- **Systematic Literature Review**: All scores based on comprehensive research analysis
- **Regular Updates**: Continuous monitoring of new research and evidence
- **Transparent Methodology**: Open documentation of scoring criteria and rationale
- **Conservative Ratings**: Protective approach against overpromising benefits
- **Expert Review**: Scientific advisory board oversight of scoring decisions
- **Peer Validation**: Cross-verification with established research databases

This evidence-based approach positions GutIntel as the definitive source for gut health intelligence, suitable for healthcare providers, researchers, and regulatory environments while maintaining commercial viability.

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Run setup script
python setup.py

# Run tests
pytest

# Code formatting
black .
isort .

# Type checking
mypy .

# Linting
flake8
```

### Database Management

The project uses PostgreSQL with a comprehensive schema supporting:
- UUID primary keys
- JSONB for flexible data storage
- Custom enums for data integrity
- Triggers for automated timestamp updates
- Proper foreign key relationships

### Configuration

All configuration is managed through environment variables with sensible defaults. The configuration system supports:
- Database connection settings
- API server configuration
- Security settings
- External API keys
- Logging configuration
- Rate limiting
- CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[License information to be added]

## Support

For questions, issues, or contributions, please [create an issue](link-to-issues) or contact the development team.