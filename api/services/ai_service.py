"""
AI Service for GutIntel API.

This module provides OpenAI integration for generating natural language explanations,
personalized recommendations, and intelligent analysis of gut health data.
"""

import json
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
from fastapi import HTTPException, status

from .. import simple_config
from ..models.ai_models import (
    UserProfile,
    MealAnalysisRequest,
    MealAnalysisResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    RecommendationRequest,
    RecommendationResponse,
    IngredientRecommendation,
    ExplanationRequest,
    ExplanationResponse
)


class AIService:
    """Service for AI-powered gut health analysis and recommendations."""
    
    def __init__(self):
        """Initialize the AI service with OpenAI client."""
        if not simple_config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=simple_config.OPENAI_API_KEY)
        self.model = simple_config.OPENAI_MODEL
    
    async def generate_explanation(self, request: ExplanationRequest) -> ExplanationResponse:
        """
        Generate natural language explanation for ingredient data.
        
        Args:
            request: Explanation request containing ingredient data
            
        Returns:
            Natural language explanation with practical advice
        """
        try:
            # Build context from ingredient data
            context = self._build_ingredient_context(request.ingredient_data)
            
            prompt = f"""
            You are a gut health expert. Explain this ingredient in simple, practical terms:
            
            INGREDIENT DATA:
            {context}
            
            TASK: Create a user-friendly explanation that includes:
            1. What this ingredient is and why it matters for gut health
            2. How it works in the body (mechanisms)
            3. Expected benefits and timeline
            4. Practical usage advice (dosage, timing, food combinations)
            5. Who should consider it and any precautions
            
            Keep it conversational, evidence-based, and actionable. Use bullet points for key information.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            explanation = response.choices[0].message.content
            
            return ExplanationResponse(
                ingredient_name=request.ingredient_data.get("name", "Unknown"),
                explanation=explanation,
                key_benefits=self._extract_benefits(request.ingredient_data),
                recommended_dosage=str(request.ingredient_data.get("dosage_info", "Consult healthcare provider")),
                timeline_expectation="Results typically seen in 2-8 weeks with consistent use"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate explanation: {str(e)}"
            )
    
    async def generate_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Generate personalized ingredient recommendations based on user profile.
        
        Args:
            request: Recommendation request with user profile and goals
            
        Returns:
            Personalized recommendations with rationale
        """
        try:
            # Build user context
            user_context = self._build_user_context(request.user_profile)
            
            prompt = f"""
            You are a personalized gut health advisor. Based on this user profile, recommend the top 5 ingredients:
            
            USER PROFILE:
            {user_context}
            
            AVAILABLE INGREDIENTS: You have access to 85+ gut health ingredients including probiotics, prebiotics, 
            digestive enzymes, and therapeutic compounds. Consider ingredients like:
            - Lactobacillus strains for digestive issues
            - Inulin/FOS for prebiotic support
            - Butyrate for gut barrier function
            - Digestive enzymes for digestion
            - Berberine for metabolic health
            
            TASK: Provide 5 personalized recommendations with:
            1. Ingredient name and why it's perfect for this user
            2. How it addresses their specific symptoms/goals
            3. Expected benefits and timeline
            4. Dosage and timing recommendations
            5. Priority level (1-5, where 1 is highest priority)
            
            Format as a structured response focusing on the user's specific needs.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.8
            )
            
            recommendations_text = response.choices[0].message.content
            
            # Parse recommendations (in production, you'd use structured output)
            recommendations = self._parse_recommendations(recommendations_text)
            
            return RecommendationResponse(
                recommendations=recommendations,
                rationale=f"Based on your symptoms ({', '.join(request.user_profile.symptoms)}) and goals ({', '.join(request.user_profile.goals)})",
                confidence_score=0.85
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate recommendations: {str(e)}"
            )
    
    async def analyze_meal(self, request: MealAnalysisRequest) -> MealAnalysisResponse:
        """
        Analyze meal ingredients for gut health impact and interactions.
        
        Args:
            request: Meal analysis request with ingredients
            
        Returns:
            Comprehensive meal analysis with gut score and recommendations
        """
        try:
            # Build meal context
            meal_context = self._build_meal_context(request.ingredients)
            
            prompt = f"""
            You are a gut health nutritionist analyzing this meal/supplement combination:
            
            MEAL INGREDIENTS:
            {meal_context}
            
            TASK: Analyze this combination for:
            1. Overall gut health score (1-10)
            2. Synergistic effects between ingredients
            3. Potential negative interactions
            4. Missing nutrients or beneficial compounds
            5. Optimization suggestions
            6. Best timing for consumption
            
            Consider:
            - Probiotic + prebiotic synergy
            - Digestive enzyme compatibility
            - Nutrient absorption interactions
            - Gut microbiome diversity support
            
            Provide actionable insights and a clear gut health score with justification.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            # Calculate composite gut score
            gut_score = self._calculate_meal_gut_score(request.ingredients)
            
            return MealAnalysisResponse(
                gut_score=gut_score,
                analysis=analysis,
                synergistic_effects=self._identify_synergies(request.ingredients),
                potential_issues=self._identify_issues(request.ingredients),
                optimization_suggestions=self._generate_optimizations(analysis),
                best_timing="Take with meals for better absorption"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze meal: {str(e)}"
            )
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Handle conversational Q&A about gut health.
        
        Args:
            request: Chat request with message and conversation history
            
        Returns:
            AI response with relevant information
        """
        try:
            # Build conversation context
            messages = self._build_conversation_context(request.messages)
            
            # Add system prompt for gut health expertise
            system_prompt = """
            You are a knowledgeable gut health advisor with access to comprehensive ingredient data.
            Provide accurate, evidence-based advice about gut health, probiotics, prebiotics, and digestive wellness.
            
            Always:
            - Base recommendations on scientific evidence
            - Suggest consulting healthcare providers for medical conditions
            - Explain mechanisms when relevant
            - Provide practical, actionable advice
            - Reference specific ingredients from the database when appropriate
            
            Keep responses conversational but informative.
            """
            
            messages.insert(0, {"role": "system", "content": system_prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return ChatResponse(
                response=ai_response,
                suggestions=self._generate_follow_up_suggestions(request.messages[-1].content),
                confidence_score=0.9
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process chat: {str(e)}"
            )
    
    def _build_ingredient_context(self, ingredient_data: Dict[str, Any]) -> str:
        """Build context string from ingredient data."""
        context = f"Name: {ingredient_data.get('name', 'Unknown')}\n"
        context += f"Category: {ingredient_data.get('category', 'Unknown')}\n"
        context += f"Gut Score: {ingredient_data.get('gut_score', 'Unknown')}/10\n"
        context += f"Confidence: {ingredient_data.get('confidence_score', 'Unknown')}\n"
        context += f"Description: {ingredient_data.get('description', 'No description')}\n"
        
        if 'effects' in ingredient_data:
            context += "\nEffects:\n"
            effects = ingredient_data['effects']
            
            if 'microbiome_effects' in effects:
                context += "Microbiome Effects:\n"
                for effect in effects['microbiome_effects'][:5]:  # Limit to top 5
                    context += f"- {effect.get('bacteria_name', 'Unknown')}: {effect.get('effect_type', 'Unknown')}\n"
            
            if 'symptom_effects' in effects:
                context += "Symptom Effects:\n"
                for effect in effects['symptom_effects'][:5]:  # Limit to top 5
                    context += f"- {effect.get('symptom_name', 'Unknown')}: {effect.get('effect_direction', 'Unknown')}\n"
        
        return context
    
    def _build_user_context(self, user_profile: UserProfile) -> str:
        """Build context string from user profile."""
        context = f"Symptoms: {', '.join(user_profile.symptoms)}\n"
        context += f"Goals: {', '.join(user_profile.goals)}\n"
        context += f"Dietary Restrictions: {', '.join(user_profile.dietary_restrictions)}\n"
        context += f"Current Supplements: {', '.join(user_profile.current_supplements)}\n"
        context += f"Age: {user_profile.age}\n"
        context += f"Gender: {user_profile.gender}\n"
        return context
    
    def _build_meal_context(self, ingredients: List[str]) -> str:
        """Build context string from meal ingredients."""
        return f"Ingredients: {', '.join(ingredients)}\n"
    
    def _build_conversation_context(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """Build conversation context for OpenAI."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-10:]  # Keep last 10 messages for context
        ]
    
    def _extract_benefits(self, ingredient_data: Dict[str, Any]) -> List[str]:
        """Extract key benefits from ingredient data."""
        benefits = []
        
        if 'effects' in ingredient_data:
            effects = ingredient_data['effects']
            
            # Extract top symptom improvements
            if 'symptom_effects' in effects:
                for effect in effects['symptom_effects'][:3]:
                    if effect.get('effect_direction') == 'improvement':
                        benefits.append(f"Improves {effect.get('symptom_name', 'symptoms')}")
            
            # Extract top microbiome benefits
            if 'microbiome_effects' in effects:
                for effect in effects['microbiome_effects'][:2]:
                    if effect.get('effect_type') == 'increases':
                        benefits.append(f"Increases {effect.get('bacteria_name', 'beneficial bacteria')}")
        
        return benefits[:5]  # Top 5 benefits
    
    def _parse_recommendations(self, text: str) -> List[IngredientRecommendation]:
        """Parse recommendations from AI response."""
        # This is a simplified parser - in production, use structured output
        
        # Mock recommendations based on common patterns
        mock_recommendations = [
            IngredientRecommendation(
                ingredient="Lactobacillus rhamnosus GG",
                reason="Excellent for digestive health and immune support",
                priority=1,
                dosage="1-2 billion CFU daily",
                timing="With meals or as directed",
                expected_benefits=["Improved digestion", "Enhanced immunity"],
                timeline="2-4 weeks for noticeable improvements",
                confidence=0.85
            ),
            IngredientRecommendation(
                ingredient="Inulin",
                reason="Prebiotic fiber to feed beneficial bacteria",
                priority=2,
                dosage="5-10g daily",
                timing="Start with 2-3g, increase gradually",
                expected_benefits=["Better gut microbiome", "Improved fiber intake"],
                timeline="3-6 weeks for microbiome changes",
                confidence=0.80
            )
        ]
        
        return mock_recommendations
    
    def _calculate_meal_gut_score(self, ingredients: List[str]) -> float:
        """Calculate composite gut score for meal."""
        # Simplified scoring - in production, use actual ingredient data
        base_score = 5.0
        
        # Award points for beneficial ingredients
        probiotic_keywords = ['lactobacillus', 'bifidobacterium', 'probiotic']
        prebiotic_keywords = ['inulin', 'fos', 'prebiotic', 'fiber']
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            if any(keyword in ingredient_lower for keyword in probiotic_keywords):
                base_score += 1.0
            if any(keyword in ingredient_lower for keyword in prebiotic_keywords):
                base_score += 0.8
        
        return min(base_score, 10.0)
    
    def _identify_synergies(self, ingredients: List[str]) -> List[str]:
        """Identify synergistic effects between ingredients."""
        synergies = []
        
        # Check for probiotic + prebiotic synergy
        has_probiotic = any('probiotic' in ing.lower() or 'lactobacillus' in ing.lower() for ing in ingredients)
        has_prebiotic = any('prebiotic' in ing.lower() or 'inulin' in ing.lower() for ing in ingredients)
        
        if has_probiotic and has_prebiotic:
            synergies.append("Probiotic + Prebiotic synergy enhances beneficial bacteria growth")
        
        return synergies
    
    def _identify_issues(self, ingredients: List[str]) -> List[str]:
        """Identify potential issues with ingredient combination."""
        issues = []
        
        # Check for potential conflicts (simplified)
        if len(ingredients) > 5:
            issues.append("High number of ingredients may cause digestive sensitivity")
        
        return issues
    
    def _generate_optimizations(self, analysis: str) -> List[str]:
        """Generate optimization suggestions from analysis."""
        optimizations = [
            "Consider spacing out supplements throughout the day",
            "Take with meals to improve absorption",
            "Start with lower doses and gradually increase"
        ]
        
        return optimizations
    
    def _generate_follow_up_suggestions(self, last_message: str) -> List[str]:
        """Generate follow-up suggestions based on last message."""
        suggestions = [
            "Would you like specific ingredient recommendations?",
            "Should I explain how these ingredients work?",
            "Do you have any dietary restrictions to consider?"
        ]
        
        return suggestions


# Global AI service instance
ai_service = AIService()