"""
AI-related Pydantic models for GutIntel API.

This module defines request and response models for AI-powered endpoints
including explanations, recommendations, meal analysis, and chat.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserProfile(BaseModel):
    """User profile for personalized recommendations."""
    
    symptoms: List[str] = Field(
        default_factory=list,
        description="Current gut health symptoms (e.g., 'bloating', 'irregular_bowel', 'low_energy')"
    )
    goals: List[str] = Field(
        default_factory=list,
        description="Health goals (e.g., 'improve_digestion', 'boost_immunity', 'weight_management')"
    )
    dietary_restrictions: List[str] = Field(
        default_factory=list,
        description="Dietary restrictions (e.g., 'vegetarian', 'dairy_free', 'gluten_free')"
    )
    current_supplements: List[str] = Field(
        default_factory=list,
        description="Current supplements or medications"
    )
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    gender: Optional[str] = Field(None, description="Gender (optional)")
    activity_level: Optional[str] = Field(
        None, 
        description="Activity level (sedentary, moderate, active, very_active)"
    )


class ExplanationRequest(BaseModel):
    """Request for natural language explanation of ingredient data."""
    
    ingredient_data: Dict[str, Any] = Field(
        description="Complete ingredient data including effects and citations"
    )
    user_level: str = Field(
        default="general",
        description="Explanation level: 'beginner', 'general', 'advanced'"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Areas to focus on (e.g., 'mechanisms', 'benefits', 'dosage')"
    )


class ExplanationResponse(BaseModel):
    """Response with natural language explanation."""
    
    ingredient_name: str = Field(description="Name of the ingredient")
    explanation: str = Field(description="Natural language explanation")
    key_benefits: List[str] = Field(description="Key benefits highlighted")
    recommended_dosage: str = Field(description="Dosage recommendations")
    timeline_expectation: str = Field(description="Expected timeline for results")
    precautions: List[str] = Field(
        default_factory=list,
        description="Important precautions or warnings"
    )
    confidence_score: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in the explanation (0-1)"
    )


class RecommendationRequest(BaseModel):
    """Request for personalized ingredient recommendations."""
    
    user_profile: UserProfile = Field(description="User's health profile")
    max_recommendations: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of recommendations to return"
    )
    budget_range: Optional[str] = Field(
        None,
        description="Budget range (e.g., 'low', 'medium', 'high')"
    )
    exclude_ingredients: List[str] = Field(
        default_factory=list,
        description="Ingredients to exclude from recommendations"
    )


class IngredientRecommendation(BaseModel):
    """Individual ingredient recommendation."""
    
    ingredient: str = Field(description="Ingredient name")
    reason: str = Field(description="Why this ingredient is recommended")
    priority: int = Field(ge=1, le=5, description="Priority level (1=highest)")
    dosage: str = Field(description="Recommended dosage")
    timing: str = Field(description="When to take it")
    expected_benefits: List[str] = Field(description="Expected benefits")
    timeline: str = Field(description="Expected timeline for results")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in recommendation")


class RecommendationResponse(BaseModel):
    """Response with personalized recommendations."""
    
    recommendations: List[IngredientRecommendation] = Field(
        description="List of personalized recommendations"
    )
    rationale: str = Field(description="Overall rationale for recommendations")
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in recommendations"
    )
    follow_up_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for follow-up actions"
    )


class MealAnalysisRequest(BaseModel):
    """Request for meal/supplement combination analysis."""
    
    ingredients: List[str] = Field(
        min_items=1,
        description="List of ingredients/supplements in the meal"
    )
    meal_type: str = Field(
        default="supplement",
        description="Type of meal: 'breakfast', 'lunch', 'dinner', 'snack', 'supplement'"
    )
    user_profile: Optional[UserProfile] = Field(
        None,
        description="User profile for personalized analysis"
    )


class MealAnalysisResponse(BaseModel):
    """Response with meal analysis results."""
    
    gut_score: float = Field(
        ge=0.0,
        le=10.0,
        description="Overall gut health score for this meal (0-10)"
    )
    analysis: str = Field(description="Detailed analysis of the meal")
    synergistic_effects: List[str] = Field(
        description="Positive interactions between ingredients"
    )
    potential_issues: List[str] = Field(
        description="Potential negative interactions or concerns"
    )
    optimization_suggestions: List[str] = Field(
        description="Suggestions to optimize gut health impact"
    )
    best_timing: str = Field(description="Recommended timing for consumption")
    missing_nutrients: List[str] = Field(
        default_factory=list,
        description="Important nutrients that could be added"
    )


class ChatMessage(BaseModel):
    """Individual chat message."""
    
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Message timestamp")


class ChatRequest(BaseModel):
    """Request for conversational Q&A."""
    
    messages: List[ChatMessage] = Field(
        description="Conversation history including current message"
    )
    user_profile: Optional[UserProfile] = Field(
        None,
        description="User profile for personalized responses"
    )
    context: Optional[str] = Field(
        None,
        description="Additional context for the conversation"
    )


class ChatResponse(BaseModel):
    """Response from conversational AI."""
    
    response: str = Field(description="AI response to the question")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Follow-up questions or suggestions"
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the response"
    )
    related_ingredients: List[str] = Field(
        default_factory=list,
        description="Related ingredients mentioned in the response"
    )


class AIHealthRequest(BaseModel):
    """Request to check AI service health."""
    
    test_query: str = Field(
        default="What is gut health?",
        description="Test query to verify AI service functionality"
    )


class AIHealthResponse(BaseModel):
    """Response from AI service health check."""
    
    status: str = Field(description="Service status: 'healthy', 'degraded', 'unhealthy'")
    model: str = Field(description="AI model being used")
    response_time_ms: float = Field(description="Response time in milliseconds")
    test_response: str = Field(description="Response to test query")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")


class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis of multiple ingredients."""
    
    ingredients: List[str] = Field(
        min_items=1,
        max_items=20,
        description="List of ingredients to analyze"
    )
    analysis_type: str = Field(
        default="summary",
        description="Type of analysis: 'summary', 'detailed', 'interactions'"
    )
    user_profile: Optional[UserProfile] = Field(
        None,
        description="User profile for personalized analysis"
    )


class BatchAnalysisResponse(BaseModel):
    """Response with batch analysis results."""
    
    individual_scores: Dict[str, float] = Field(
        description="Individual gut scores for each ingredient"
    )
    combined_score: float = Field(
        ge=0.0,
        le=10.0,
        description="Combined gut health score"
    )
    analysis_summary: str = Field(description="Summary of the batch analysis")
    top_synergies: List[str] = Field(description="Top synergistic combinations")
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about combinations"
    )
    optimization_suggestions: List[str] = Field(
        description="Suggestions to optimize the combination"
    )