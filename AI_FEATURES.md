# GutIntel AI Features Documentation

## Overview

GutIntel Phase 2 has successfully integrated OpenAI GPT-4 to transform your gut health ingredient database into an intelligent, personalized platform. The AI layer provides natural language explanations, personalized recommendations, meal analysis, and conversational Q&A capabilities.

## 🚀 New AI Endpoints

### 1. Natural Language Explanations
**Endpoint:** `POST /api/v1/ai/explain`

Transform technical ingredient data into user-friendly explanations with practical advice.

```json
{
  "ingredient_name": "inulin",
  "user_level": "general"
}
```

**Features:**
- Converts scientific data into conversational explanations
- Provides practical usage advice and timelines
- Explains mechanisms in accessible language
- Includes dosage recommendations and precautions

### 2. Personalized Recommendations
**Endpoint:** `POST /api/v1/ai/recommend`

Generate tailored ingredient recommendations based on user symptoms, goals, and restrictions.

```json
{
  "user_profile": {
    "symptoms": ["bloating", "irregular_bowel"],
    "goals": ["improve_digestion", "boost_immunity"],
    "dietary_restrictions": ["vegetarian"],
    "current_supplements": ["multivitamin"],
    "age": 35,
    "gender": "female"
  },
  "max_recommendations": 5
}
```

**Features:**
- Symptom-to-ingredient mapping
- Goal-oriented recommendations
- Dietary restriction compliance
- Supplement interaction awareness
- Prioritized suggestions with confidence scores

### 3. Intelligent Meal Analysis
**Endpoint:** `POST /api/v1/ai/analyze-meal`

Analyze ingredient combinations for gut health impact and optimization opportunities.

```json
{
  "ingredients": ["inulin", "lactobacillus", "psyllium husk"],
  "meal_type": "supplement",
  "user_profile": {...}
}
```

**Features:**
- Combined gut health scoring (0-10)
- Synergistic effect detection
- Interaction warnings
- Optimization suggestions
- Timing recommendations

### 4. Conversational Q&A
**Endpoint:** `POST /api/v1/ai/chat`

Chat interface for complex gut health questions with conversation memory.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What are the best probiotics for digestive health?",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "user_profile": {...}
}
```

**Features:**
- Context-aware responses
- Ingredient database integration
- Follow-up suggestions
- Personalized advice
- Conversation history support

### 5. Batch Analysis
**Endpoint:** `POST /api/v1/ai/batch-analyze`

Analyze multiple ingredients simultaneously for comprehensive insights.

```json
{
  "ingredients": ["inulin", "berberine", "omega-3", "vitamin-d"],
  "analysis_type": "summary",
  "user_profile": {...}
}
```

### 6. AI Health Check
**Endpoint:** `GET /api/v1/ai/health`

Monitor AI service health and performance.

### 7. AI Capabilities
**Endpoint:** `GET /api/v1/ai/capabilities`

Get information about available AI features and limitations.

## 🧠 AI Service Architecture

### Core Components

1. **AI Service (`ai_service.py`)**
   - OpenAI GPT-4 integration
   - Prompt engineering for gut health domain
   - Response processing and validation

2. **Meal Analyzer (`meal_analyzer.py`)**
   - Ingredient interaction detection
   - Gut health scoring algorithms
   - Optimization recommendations

3. **AI Models (`ai_models.py`)**
   - Pydantic models for all AI requests/responses
   - User profile management
   - Conversation history tracking

4. **AI Router (`ai.py`)**
   - FastAPI endpoints for all AI features
   - Error handling and validation
   - Database integration

## 🛠️ Technical Implementation

### Prompt Engineering
Each AI endpoint uses specialized prompts optimized for gut health:

- **Explanation prompts**: Focus on practical, actionable advice
- **Recommendation prompts**: Consider user symptoms, goals, and restrictions
- **Analysis prompts**: Evaluate ingredient interactions and synergies
- **Chat prompts**: Maintain conversation context and expertise

### Meal Analysis Algorithm
1. **Base Scoring**: Individual ingredient gut health scores
2. **Interaction Detection**: Synergistic and antagonistic effects
3. **Diversity Bonus**: Rewards for ingredient variety
4. **Final Score**: Weighted combination with 0-10 range

### User Profiling
Comprehensive user profiles include:
- Symptoms and health goals
- Dietary restrictions and preferences
- Current supplements and medications
- Demographics (age, gender, activity level)

## 📊 Response Format

All AI endpoints return structured responses with:
- **Success/Error status**
- **Confidence scores**
- **Detailed explanations**
- **Actionable recommendations**
- **Follow-up suggestions**

Example response:
```json
{
  "success": true,
  "data": {
    "explanation": "Inulin is a prebiotic fiber that...",
    "key_benefits": ["Feeds beneficial bacteria", "Improves digestion"],
    "recommended_dosage": "5-10g daily",
    "confidence_score": 0.9
  },
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "abc123"
  }
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Required for AI features
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Optional AI configuration
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000
AI_TIMEOUT=30
```

### Dependencies
```bash
pip install openai>=1.12.0
```

## 🧪 Testing

Use the provided test script to validate AI functionality:

```bash
python test_ai_endpoints.py
```

The script tests:
- All AI endpoints
- Response formats
- Error handling
- Performance metrics

## 🚨 Important Notes

### Security & Privacy
- Never log or store OpenAI API keys
- User profiles are processed but not permanently stored
- All AI responses include disclaimers about medical advice

### Rate Limiting
- OpenAI API has rate limits
- Implement caching for repeated queries
- Monitor usage and costs

### Error Handling
- Graceful degradation when AI service is unavailable
- Clear error messages for users
- Fallback responses for common queries

## 🎯 Key Benefits

1. **Enhanced User Experience**: Complex data becomes conversational
2. **Personalization**: Tailored recommendations based on individual needs
3. **Intelligent Analysis**: Ingredient interactions and optimizations
4. **Scalability**: AI handles complex queries automatically
5. **Accessibility**: Scientific data becomes understandable to everyone

## 🔮 Future Enhancements

- **Multi-language support**
- **Voice interface integration**
- **Advanced user profiling with health tracking**
- **Integration with wearable devices**
- **Predictive health modeling**

## 📋 Implementation Checklist

- ✅ OpenAI integration setup
- ✅ AI service layer created
- ✅ Prompt engineering for gut health domain
- ✅ Natural language explanation endpoint
- ✅ Personalized recommendation engine
- ✅ Meal analysis functionality
- ✅ Conversational Q&A interface
- ✅ User profiling system
- ✅ Error handling and validation
- ✅ Testing framework
- ✅ Documentation

Your GutIntel API has been successfully transformed from a data service into an intelligent gut health platform! 🎉