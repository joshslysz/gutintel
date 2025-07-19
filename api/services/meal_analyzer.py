"""
Meal Analysis Service for GutIntel API.

This module provides specialized logic for analyzing meal and supplement combinations,
detecting interactions, and calculating combined gut health scores.
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class InteractionType(Enum):
    """Types of ingredient interactions."""
    SYNERGISTIC = "synergistic"
    ANTAGONISTIC = "antagonistic"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class InteractionStrength(Enum):
    """Strength of ingredient interactions."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


@dataclass
class IngredientInteraction:
    """Represents an interaction between two ingredients."""
    ingredient1: str
    ingredient2: str
    interaction_type: InteractionType
    strength: InteractionStrength
    description: str
    confidence: float
    mechanism: Optional[str] = None


@dataclass
class MealScore:
    """Represents the gut health score for a meal."""
    total_score: float
    individual_scores: Dict[str, float]
    interaction_bonus: float
    interaction_penalty: float
    diversity_bonus: float


class MealAnalyzer:
    """Analyzes meals and supplement combinations for gut health impact."""
    
    def __init__(self):
        """Initialize the meal analyzer with interaction rules."""
        self.interaction_rules = self._load_interaction_rules()
        self.category_weights = self._load_category_weights()
        self.ingredient_categories = self._load_ingredient_categories()
    
    def analyze_meal(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a meal or supplement combination.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            Comprehensive analysis including scores, interactions, and recommendations
        """
        # Calculate gut health score
        meal_score = self.calculate_meal_score(ingredients)
        
        # Detect interactions
        interactions = self.detect_interactions(ingredients)
        
        # Analyze diversity
        diversity_analysis = self.analyze_diversity(ingredients)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(ingredients, meal_score, interactions)
        
        # Identify timing considerations
        timing_analysis = self.analyze_timing(ingredients)
        
        return {
            "gut_score": meal_score.total_score,
            "individual_scores": meal_score.individual_scores,
            "interactions": {
                "synergistic": [i for i in interactions if i.interaction_type == InteractionType.SYNERGISTIC],
                "antagonistic": [i for i in interactions if i.interaction_type == InteractionType.ANTAGONISTIC],
                "neutral": [i for i in interactions if i.interaction_type == InteractionType.NEUTRAL]
            },
            "diversity": diversity_analysis,
            "recommendations": recommendations,
            "timing": timing_analysis,
            "warnings": self._generate_warnings(ingredients, interactions)
        }
    
    def calculate_meal_score(self, ingredients: List[str]) -> MealScore:
        """
        Calculate the overall gut health score for a meal.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            MealScore with detailed scoring breakdown
        """
        # Base scores for individual ingredients
        individual_scores = {}
        total_base_score = 0
        
        for ingredient in ingredients:
            base_score = self._get_ingredient_base_score(ingredient)
            individual_scores[ingredient] = base_score
            total_base_score += base_score
        
        # Average base score
        avg_base_score = total_base_score / len(ingredients) if ingredients else 0
        
        # Calculate interaction effects
        interactions = self.detect_interactions(ingredients)
        interaction_bonus = sum(
            self._calculate_interaction_bonus(interaction)
            for interaction in interactions
            if interaction.interaction_type == InteractionType.SYNERGISTIC
        )
        interaction_penalty = sum(
            self._calculate_interaction_penalty(interaction)
            for interaction in interactions
            if interaction.interaction_type == InteractionType.ANTAGONISTIC
        )
        
        # Calculate diversity bonus
        diversity_bonus = self._calculate_diversity_bonus(ingredients)
        
        # Calculate final score
        final_score = avg_base_score + interaction_bonus - interaction_penalty + diversity_bonus
        final_score = max(0, min(10, final_score))  # Clamp to 0-10 range
        
        return MealScore(
            total_score=final_score,
            individual_scores=individual_scores,
            interaction_bonus=interaction_bonus,
            interaction_penalty=interaction_penalty,
            diversity_bonus=diversity_bonus
        )
    
    def detect_interactions(self, ingredients: List[str]) -> List[IngredientInteraction]:
        """
        Detect interactions between ingredients.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            List of detected interactions
        """
        interactions = []
        
        # Check each pair of ingredients
        for i, ingredient1 in enumerate(ingredients):
            for ingredient2 in ingredients[i+1:]:
                interaction = self._check_interaction(ingredient1, ingredient2)
                if interaction:
                    interactions.append(interaction)
        
        return interactions
    
    def analyze_diversity(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Analyze the diversity of ingredient categories.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            Diversity analysis including category distribution
        """
        categories = [self._get_ingredient_category(ing) for ing in ingredients]
        category_counts = {}
        
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        total_categories = len(set(categories))
        diversity_score = min(total_categories / 4, 1.0)  # Normalize to 0-1
        
        return {
            "category_distribution": category_counts,
            "unique_categories": total_categories,
            "diversity_score": diversity_score,
            "recommendations": self._generate_diversity_recommendations(category_counts)
        }
    
    def generate_recommendations(
        self, 
        ingredients: List[str], 
        meal_score: MealScore, 
        interactions: List[IngredientInteraction]
    ) -> List[str]:
        """
        Generate optimization recommendations for the meal.
        
        Args:
            ingredients: List of ingredient names
            meal_score: Calculated meal score
            interactions: Detected interactions
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Score-based recommendations
        if meal_score.total_score < 5:
            recommendations.append("Consider adding more high-impact gut health ingredients")
        
        # Interaction-based recommendations
        antagonistic_interactions = [
            i for i in interactions 
            if i.interaction_type == InteractionType.ANTAGONISTIC
        ]
        
        if antagonistic_interactions:
            recommendations.append("Consider spacing out conflicting ingredients throughout the day")
        
        # Diversity-based recommendations
        categories = [self._get_ingredient_category(ing) for ing in ingredients]
        if "prebiotic" not in categories and "probiotic" in categories:
            recommendations.append("Add prebiotic fiber to support probiotic effectiveness")
        
        if "probiotic" not in categories and "prebiotic" in categories:
            recommendations.append("Consider adding probiotics to work with prebiotic fibers")
        
        # Dosage recommendations
        if len(ingredients) > 7:
            recommendations.append("Consider reducing the number of ingredients to avoid digestive overwhelm")
        
        return recommendations
    
    def analyze_timing(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Analyze optimal timing for ingredient consumption.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            Timing analysis and recommendations
        """
        timing_groups = {
            "with_meals": [],
            "empty_stomach": [],
            "before_bed": [],
            "morning": [],
            "anytime": []
        }
        
        for ingredient in ingredients:
            optimal_timing = self._get_optimal_timing(ingredient)
            timing_groups[optimal_timing].append(ingredient)
        
        return {
            "timing_groups": timing_groups,
            "recommendations": self._generate_timing_recommendations(timing_groups),
            "potential_conflicts": self._identify_timing_conflicts(timing_groups)
        }
    
    def _load_interaction_rules(self) -> Dict[Tuple[str, str], IngredientInteraction]:
        """Load predefined interaction rules."""
        # In production, this would load from a database or configuration file
        return {
            ("probiotic", "prebiotic"): IngredientInteraction(
                ingredient1="probiotic",
                ingredient2="prebiotic",
                interaction_type=InteractionType.SYNERGISTIC,
                strength=InteractionStrength.STRONG,
                description="Prebiotics feed probiotics, enhancing their effectiveness",
                confidence=0.9,
                mechanism="Prebiotic fibers provide nutrients for probiotic bacteria"
            ),
            ("calcium", "iron"): IngredientInteraction(
                ingredient1="calcium",
                ingredient2="iron",
                interaction_type=InteractionType.ANTAGONISTIC,
                strength=InteractionStrength.MODERATE,
                description="Calcium can reduce iron absorption",
                confidence=0.8,
                mechanism="Calcium competes with iron for absorption pathways"
            ),
            ("digestive_enzyme", "protein"): IngredientInteraction(
                ingredient1="digestive_enzyme",
                ingredient2="protein",
                interaction_type=InteractionType.SYNERGISTIC,
                strength=InteractionStrength.MODERATE,
                description="Digestive enzymes improve protein digestion",
                confidence=0.85,
                mechanism="Enzymes break down proteins into absorbable amino acids"
            )
        }
    
    def _load_category_weights(self) -> Dict[str, float]:
        """Load category weights for scoring."""
        return {
            "probiotic": 8.5,
            "prebiotic": 7.8,
            "digestive_enzyme": 7.2,
            "postbiotic": 8.0,
            "therapeutic": 6.5,
            "fiber": 7.0,
            "antioxidant": 6.8,
            "mineral": 6.0,
            "vitamin": 5.8,
            "herb": 6.2
        }
    
    def _load_ingredient_categories(self) -> Dict[str, str]:
        """Load ingredient category mappings."""
        return {
            "lactobacillus": "probiotic",
            "bifidobacterium": "probiotic",
            "saccharomyces": "probiotic",
            "inulin": "prebiotic",
            "fos": "prebiotic",
            "gos": "prebiotic",
            "psyllium": "fiber",
            "butyrate": "postbiotic",
            "digestive_enzymes": "digestive_enzyme",
            "glutamine": "therapeutic",
            "zinc": "mineral",
            "magnesium": "mineral",
            "vitamin_d": "vitamin",
            "curcumin": "antioxidant",
            "berberine": "therapeutic",
            "ginger": "herb",
            "peppermint": "herb"
        }
    
    def _get_ingredient_base_score(self, ingredient: str) -> float:
        """Get base gut health score for an ingredient."""
        # Normalize ingredient name
        normalized = ingredient.lower().replace(" ", "_").replace("-", "_")
        
        # Check for exact matches first
        if normalized in self.ingredient_categories:
            category = self.ingredient_categories[normalized]
            return self.category_weights.get(category, 6.0)
        
        # Check for partial matches
        for key, category in self.ingredient_categories.items():
            if key in normalized or normalized in key:
                return self.category_weights.get(category, 6.0)
        
        # Default score for unknown ingredients
        return 5.0
    
    def _get_ingredient_category(self, ingredient: str) -> str:
        """Get category for an ingredient."""
        normalized = ingredient.lower().replace(" ", "_").replace("-", "_")
        
        # Check for exact matches first
        if normalized in self.ingredient_categories:
            return self.ingredient_categories[normalized]
        
        # Check for partial matches
        for key, category in self.ingredient_categories.items():
            if key in normalized or normalized in key:
                return category
        
        return "unknown"
    
    def _check_interaction(self, ingredient1: str, ingredient2: str) -> Optional[IngredientInteraction]:
        """Check if two ingredients have a known interaction."""
        cat1 = self._get_ingredient_category(ingredient1)
        cat2 = self._get_ingredient_category(ingredient2)
        
        # Check category-based interactions
        interaction_key = (cat1, cat2) if cat1 <= cat2 else (cat2, cat1)
        
        if interaction_key in self.interaction_rules:
            interaction = self.interaction_rules[interaction_key]
            return IngredientInteraction(
                ingredient1=ingredient1,
                ingredient2=ingredient2,
                interaction_type=interaction.interaction_type,
                strength=interaction.strength,
                description=interaction.description,
                confidence=interaction.confidence,
                mechanism=interaction.mechanism
            )
        
        return None
    
    def _calculate_interaction_bonus(self, interaction: IngredientInteraction) -> float:
        """Calculate bonus score for synergistic interactions."""
        strength_multipliers = {
            InteractionStrength.WEAK: 0.2,
            InteractionStrength.MODERATE: 0.5,
            InteractionStrength.STRONG: 1.0
        }
        
        return strength_multipliers.get(interaction.strength, 0) * interaction.confidence
    
    def _calculate_interaction_penalty(self, interaction: IngredientInteraction) -> float:
        """Calculate penalty for antagonistic interactions."""
        strength_multipliers = {
            InteractionStrength.WEAK: 0.3,
            InteractionStrength.MODERATE: 0.7,
            InteractionStrength.STRONG: 1.2
        }
        
        return strength_multipliers.get(interaction.strength, 0) * interaction.confidence
    
    def _calculate_diversity_bonus(self, ingredients: List[str]) -> float:
        """Calculate bonus for ingredient diversity."""
        categories = [self._get_ingredient_category(ing) for ing in ingredients]
        unique_categories = len(set(categories))
        
        # Bonus for having multiple categories
        if unique_categories >= 4:
            return 1.0
        elif unique_categories >= 3:
            return 0.6
        elif unique_categories >= 2:
            return 0.3
        else:
            return 0.0
    
    def _generate_diversity_recommendations(self, category_counts: Dict[str, int]) -> List[str]:
        """Generate recommendations based on category diversity."""
        recommendations = []
        
        if "probiotic" not in category_counts:
            recommendations.append("Consider adding a probiotic for microbiome support")
        
        if "prebiotic" not in category_counts:
            recommendations.append("Add prebiotic fiber to feed beneficial bacteria")
        
        if "digestive_enzyme" not in category_counts:
            recommendations.append("Digestive enzymes could improve nutrient absorption")
        
        return recommendations
    
    def _get_optimal_timing(self, ingredient: str) -> str:
        """Get optimal timing for an ingredient."""
        category = self._get_ingredient_category(ingredient)
        
        timing_map = {
            "probiotic": "with_meals",
            "prebiotic": "with_meals",
            "digestive_enzyme": "with_meals",
            "mineral": "with_meals",
            "vitamin": "with_meals",
            "therapeutic": "empty_stomach",
            "herb": "anytime",
            "antioxidant": "anytime"
        }
        
        return timing_map.get(category, "anytime")
    
    def _generate_timing_recommendations(self, timing_groups: Dict[str, List[str]]) -> List[str]:
        """Generate timing recommendations."""
        recommendations = []
        
        if timing_groups["with_meals"]:
            recommendations.append(f"Take with meals: {', '.join(timing_groups['with_meals'])}")
        
        if timing_groups["empty_stomach"]:
            recommendations.append(f"Take on empty stomach: {', '.join(timing_groups['empty_stomach'])}")
        
        if timing_groups["morning"]:
            recommendations.append(f"Best taken in the morning: {', '.join(timing_groups['morning'])}")
        
        return recommendations
    
    def _identify_timing_conflicts(self, timing_groups: Dict[str, List[str]]) -> List[str]:
        """Identify timing conflicts."""
        conflicts = []
        
        if timing_groups["with_meals"] and timing_groups["empty_stomach"]:
            conflicts.append("Some ingredients need food while others need empty stomach - space them apart")
        
        return conflicts
    
    def _generate_warnings(self, ingredients: List[str], interactions: List[IngredientInteraction]) -> List[str]:
        """Generate warnings for the meal combination."""
        warnings = []
        
        # Check for too many ingredients
        if len(ingredients) > 8:
            warnings.append("High number of ingredients may cause digestive sensitivity")
        
        # Check for strong antagonistic interactions
        strong_antagonistic = [
            i for i in interactions 
            if i.interaction_type == InteractionType.ANTAGONISTIC and i.strength == InteractionStrength.STRONG
        ]
        
        if strong_antagonistic:
            warnings.append("Strong negative interactions detected - consider spacing ingredients apart")
        
        # Check for multiple probiotics
        probiotic_count = sum(1 for ing in ingredients if "probiotic" in self._get_ingredient_category(ing))
        if probiotic_count > 3:
            warnings.append("Multiple probiotics may compete - consider rotating them")
        
        return warnings


# Global meal analyzer instance
meal_analyzer = MealAnalyzer()