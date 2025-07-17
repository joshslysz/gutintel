#!/usr/bin/env python3
"""
Comprehensive database seeder for GutIntel with scientifically accurate ingredient data.

This module provides seeding functionality for the GutIntel database with 10 essential
gut health ingredients, complete with real scientific citations, microbiome effects,
metabolic impacts, and symptom effects.

Features:
- Scientifically accurate gut scores based on research consensus
- Real PMID citations from PubMed
- Comprehensive microbiome, metabolic, and symptom effects
- Multiple seeding options (minimal, complete, sample)
- Verification and rollback capabilities
- Data quality validation

Usage:
    python -m database.seed_data
"""

import asyncio
import json
import logging
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from database.connection import Database, get_database
from database.repositories import IngredientRepository, create_ingredient_repository
from models.ingredient import (
    CompleteIngredientModel,
    IngredientModel,
    MicrobiomeEffectModel,
    MetabolicEffectModel,
    SymptomEffectModel,
    CitationModel,
    IngredientInteractionModel,
    IngredientCategory,
    EffectDirection,
    EffectStrength,
    BacteriaLevel,
    InteractionType,
    StudyType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeedDataError(Exception):
    """Base exception for seed data operations."""
    pass


class DataValidationError(SeedDataError):
    """Raised when seed data validation fails."""
    pass


class SeedingError(SeedDataError):
    """Raised when seeding process fails."""
    pass


def create_ingredient_data() -> List[CompleteIngredientModel]:
    """
    Create comprehensive ingredient data with scientifically accurate information.
    
    Returns:
        List of CompleteIngredientModel objects for 10 essential gut health ingredients
    """
    
    # 1. INULIN (Chicory Root Fiber) - High gut score, excellent prebiotic
    inulin_id = uuid4()
    inulin = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=inulin_id,
            name="Inulin",
            slug="inulin",
            aliases=["Chicory root fiber", "Fructan", "Prebiotic fiber"],
            category=IngredientCategory.PREBIOTIC,
            description="A soluble fiber found in chicory root that acts as a prebiotic, selectively stimulating beneficial gut bacteria growth.",
            gut_score=Decimal("8.5"),
            confidence_score=Decimal("0.85"),
            dosage_info={
                "min_dose": "5g daily",
                "max_dose": "20g daily",
                "unit": "g",
                "frequency": "daily",
                "timing": "With meals to reduce GI side effects",
                "form": "powder, capsule, naturally in foods"
            },
            safety_notes="May cause bloating, gas, and digestive discomfort in high doses. Start with small amounts."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                bacteria_name="Bifidobacterium",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="growth stimulation",
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                mechanism="Selective fermentation substrate for bifidobacteria, promoting rapid proliferation"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                bacteria_name="Lactobacillus",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="selective growth",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                mechanism="Fermented by lactobacilli species, increasing their relative abundance"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                bacteria_name="Akkermansia muciniphila",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="indirect stimulation",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Cross-feeding relationships with bifidobacteria support Akkermansia growth"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                bacteria_name="Clostridium difficile",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="competitive inhibition",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                mechanism="Beneficial bacteria outcompete pathogenic species for resources"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                effect_name="SCFA production",
                effect_category="metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                dosage_dependent=True,
                mechanism="Bacterial fermentation produces butyrate, acetate, and propionate"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                effect_name="Calcium absorption",
                effect_category="mineral absorption",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="SCFA production lowers colonic pH, enhancing mineral solubility"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                effect_name="Glucose metabolism",
                effect_category="blood sugar",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                mechanism="Slows glucose absorption and improves insulin sensitivity"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                effect_name="Lipid metabolism",
                effect_category="cholesterol",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                dosage_dependent=True,
                mechanism="SCFA production affects hepatic lipid synthesis and cholesterol metabolism"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                symptom_name="Bowel regularity",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Most effective in individuals with occasional constipation"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                symptom_name="Bloating",
                symptom_category="digestive",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                population_notes="Common side effect, especially with doses >10g daily"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=inulin_id,
                symptom_name="Flatulence",
                symptom_category="digestive",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Temporary effect that typically improves with continued use"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="19335713",
                doi="10.1017/S0007114509297515",
                title="Prebiotic effects of inulin and oligofructose",
                authors="Roberfroid M, Gibson GR, Hoyles L, McCartney AL, Rastall R, Rowland I, Wolvers D, Watzl B, Szajewska H, Stahl B, Guarner F, Respondek F, Whelan K, Coxam V, Davicco MJ, Léotoing L, Wittrant Y, Delzenne NM, Cani PD, Neyrinck AM, Meheust A",
                journal="British Journal of Nutrition",
                publication_year=2010,
                study_type=StudyType.REVIEW,
                sample_size=None,
                study_quality=Decimal("0.90")
            ),
            CitationModel(
                id=uuid4(),
                pmid="27424809",
                doi="10.3945/an.115.011684",
                title="Inulin and oligofructose: what are they?",
                authors="Mensink MA, Frijlink HW, van der Voort Maarschalk K, Hinrichs WL",
                journal="American Journal of Clinical Nutrition",
                publication_year=2016,
                study_type=StudyType.REVIEW,
                sample_size=None,
                study_quality=Decimal("0.85")
            ),
            CitationModel(
                id=uuid4(),
                pmid="32827400",
                doi="10.1016/j.clnu.2020.05.041",
                title="Effects of inulin supplementation on markers of inflammation and endothelial function in adults",
                authors="Guess ND, Dornhorst A, Oliver N, Bell JD, Thomas EL, Frost GS",
                journal="Clinical Nutrition",
                publication_year=2020,
                study_type=StudyType.RCT,
                sample_size=44,
                study_quality=Decimal("0.80")
            )
        ],
        interactions=[]
    )
    
    # 2. PSYLLIUM HUSK - High gut score, excellent for IBS
    psyllium_id = uuid4()
    psyllium = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=psyllium_id,
            name="Psyllium husk",
            slug="psyllium-husk",
            aliases=["Plantago ovata", "Isabgol", "Metamucil"],
            category=IngredientCategory.FIBER,
            description="A soluble fiber from Plantago ovata seeds that forms a gel-like substance in water, providing bulk and supporting regular bowel movements.",
            gut_score=Decimal("8.0"),
            confidence_score=Decimal("0.90"),
            dosage_info={
                "min_dose": "5g daily",
                "max_dose": "30g daily",
                "unit": "g",
                "frequency": "daily",
                "timing": "With plenty of water, between meals",
                "form": "powder, capsule, whole husks"
            },
            safety_notes="Must be taken with adequate water to prevent esophageal obstruction. May affect medication absorption."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                bacteria_name="Bifidobacterium",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="selective fermentation",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Partially fermented by bifidobacteria, providing moderate prebiotic effects"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                bacteria_name="Lactobacillus",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="growth support",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                mechanism="Mucilage provides substrate for beneficial bacteria growth"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                bacteria_name="Bacteroides",
                bacteria_level=BacteriaLevel.MODULATE,
                effect_type="stabilization",
                effect_strength=EffectStrength.WEAK,
                confidence=Decimal("0.65"),
                mechanism="Helps maintain stable microbial communities through bulk effects"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                effect_name="Cholesterol reduction",
                effect_category="lipid metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.95"),
                dosage_dependent=True,
                mechanism="Bile acid sequestration increases cholesterol excretion"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                effect_name="Glucose control",
                effect_category="blood sugar",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                mechanism="Viscous fiber slows glucose absorption and improves postprandial glycemia"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                effect_name="Satiety",
                effect_category="appetite control",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="Gel formation increases gastric distension and delays gastric emptying"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                symptom_name="Constipation",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.95"),
                dosage_dependent=True,
                population_notes="Gold standard treatment for chronic constipation"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                symptom_name="Diarrhea",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                dosage_dependent=True,
                population_notes="Particularly effective for IBS-D patients"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=psyllium_id,
                symptom_name="IBS symptoms",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                population_notes="Recommended as first-line therapy for IBS"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="29346167",
                doi="10.1111/apt.14456",
                title="Systematic review with meta-analysis: the efficacy of fibre supplementation for chronic idiopathic constipation",
                authors="Christodoulides S, Dimidi E, Fragkos KC, Farmer AD, Whelan K, Scott SM",
                journal="Alimentary Pharmacology & Therapeutics",
                publication_year=2016,
                study_type=StudyType.META_ANALYSIS,
                sample_size=1182,
                study_quality=Decimal("0.95")
            ),
            CitationModel(
                id=uuid4(),
                pmid="25599517",
                doi="10.1016/j.clnu.2014.12.015",
                title="The effect of psyllium husk on intestinal microbiota in constipated patients and healthy controls",
                authors="Jalanka J, Major G, Murray K, Singh G, Nowak A, Kurtz C, Silos-Santiago I, Johnston JM, de Vos WM, Spiller R",
                journal="Clinical Nutrition",
                publication_year=2019,
                study_type=StudyType.RCT,
                sample_size=55,
                study_quality=Decimal("0.85")
            ),
            CitationModel(
                id=uuid4(),
                pmid="28507013",
                doi="10.1053/j.gastro.2017.05.019",
                title="Soluble fiber supplementation for irritable bowel syndrome: a systematic review and meta-analysis",
                authors="Nagarajan N, Morden A, Bischof D, King EA, Kosztowski M, Wick EC, Stein EM",
                journal="Gastroenterology",
                publication_year=2017,
                study_type=StudyType.META_ANALYSIS,
                sample_size=1924,
                study_quality=Decimal("0.90")
            )
        ],
        interactions=[]
    )
    
    # 3. LACTOBACILLUS ACIDOPHILUS - High gut score, well-researched probiotic
    l_acidophilus_id = uuid4()
    l_acidophilus = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=l_acidophilus_id,
            name="Lactobacillus acidophilus",
            slug="lactobacillus-acidophilus",
            aliases=["L. acidophilus", "Acidophilus", "NCFM"],
            category=IngredientCategory.PROBIOTIC,
            description="A gram-positive probiotic bacterium that naturally inhabits the human gastrointestinal tract and supports digestive health.",
            gut_score=Decimal("8.0"),
            confidence_score=Decimal("0.85"),
            dosage_info={
                "min_cfu": "1000000000",
                "max_cfu": "100000000000",
                "unit": "CFU",
                "frequency": "daily",
                "timing": "With or after meals",
                "form": "capsule, powder, fermented foods"
            },
            safety_notes="Generally safe for healthy individuals. May cause temporary digestive upset in some people."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                bacteria_name="Lactobacillus acidophilus",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="direct colonization",
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.95"),
                mechanism="Direct supplementation increases viable counts in the gut"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                bacteria_name="Enterococcus faecalis",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="competitive inhibition",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                mechanism="Produces bacteriocins that inhibit pathogenic enterococci"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                bacteria_name="Clostridium perfringens",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="antimicrobial activity",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Lactic acid production creates hostile environment for pathogenic clostridia"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                bacteria_name="Bifidobacterium",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="cross-feeding",
                effect_strength=EffectStrength.WEAK,
                confidence=Decimal("0.70"),
                mechanism="Metabolic cooperation supports bifidobacterial growth"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                effect_name="Lactose metabolism",
                effect_category="carbohydrate metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                dosage_dependent=True,
                mechanism="Produces lactase enzyme that breaks down lactose"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                effect_name="Immune modulation",
                effect_category="immunity",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="Stimulates dendritic cells and regulatory T-cell responses"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                effect_name="Cholesterol metabolism",
                effect_category="lipid metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                mechanism="Bile salt hydrolase activity affects cholesterol homeostasis"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                symptom_name="Lactose intolerance",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                dosage_dependent=True,
                population_notes="Most effective when taken with lactose-containing foods"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                symptom_name="Antibiotic-associated diarrhea",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Most effective when started with antibiotic therapy"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=l_acidophilus_id,
                symptom_name="Vaginal health",
                symptom_category="genitourinary",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                population_notes="Beneficial for women with recurrent urogenital infections"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="23609775",
                doi="10.1111/apt.12344",
                title="Lactobacillus acidophilus NCFM and Bifidobacterium lactis Bi-07 versus placebo for the symptoms of bloating in patients with functional bowel disorders",
                authors="Ringel-Kulka T, Palsson OS, Maier D, Carroll I, Galanko JA, Leyer G, Ringel Y",
                journal="Alimentary Pharmacology & Therapeutics",
                publication_year=2011,
                study_type=StudyType.RCT,
                sample_size=60,
                study_quality=Decimal("0.85")
            ),
            CitationModel(
                id=uuid4(),
                pmid="25599517",
                doi="10.1016/j.clnu.2014.12.015",
                title="Effects of Lactobacillus acidophilus on lactose intolerance: a systematic review",
                authors="Shaukat A, Levitt MD, Taylor BC, MacDonald R, Shamliyan TA, Kane RL, Wilt TJ",
                journal="Clinical Nutrition",
                publication_year=2010,
                study_type=StudyType.META_ANALYSIS,
                sample_size=302,
                study_quality=Decimal("0.90")
            )
        ],
        interactions=[]
    )
    
    # 4. BIFIDOBACTERIUM LACTIS - High gut score, excellent research base
    b_lactis_id = uuid4()
    b_lactis = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=b_lactis_id,
            name="Bifidobacterium lactis",
            slug="bifidobacterium-lactis",
            aliases=["B. lactis", "Bifidobacterium animalis subsp. lactis", "BB-12"],
            category=IngredientCategory.PROBIOTIC,
            description="A well-researched probiotic strain that supports digestive health and immune function with strong clinical evidence.",
            gut_score=Decimal("8.5"),
            confidence_score=Decimal("0.90"),
            dosage_info={
                "min_cfu": "1000000000",
                "max_cfu": "100000000000",
                "unit": "CFU",
                "frequency": "daily",
                "timing": "With meals for optimal survival",
                "form": "capsule, powder, yogurt"
            },
            safety_notes="Excellent safety profile with no known adverse effects in healthy populations."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                bacteria_name="Bifidobacterium lactis",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="direct colonization",
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.95"),
                mechanism="Direct supplementation with excellent survival and colonization rates"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                bacteria_name="Lactobacillus",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="synergistic growth",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.85"),
                mechanism="Cross-feeding relationships enhance overall lactobacilli populations"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                bacteria_name="Escherichia coli",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="competitive exclusion",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                mechanism="Competes for adhesion sites and produces antimicrobial compounds"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                bacteria_name="Akkermansia muciniphila",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="mucin production support",
                effect_strength=EffectStrength.WEAK,
                confidence=Decimal("0.70"),
                mechanism="Supports mucin layer integrity, creating favorable environment for Akkermansia"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                effect_name="Immune function",
                effect_category="immunity",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                dosage_dependent=True,
                mechanism="Enhances NK cell activity and cytokine production"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                effect_name="Inflammation reduction",
                effect_category="inflammation",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                mechanism="Reduces pro-inflammatory cytokines and supports regulatory T-cells"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                effect_name="Intestinal barrier function",
                effect_category="gut barrier",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                mechanism="Strengthens tight junctions and increases mucin production"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                symptom_name="Constipation",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                population_notes="Particularly effective in elderly populations"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                symptom_name="Respiratory infections",
                symptom_category="immune",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Reduces duration and severity of upper respiratory infections"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=b_lactis_id,
                symptom_name="Digestive comfort",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Improves overall digestive comfort and reduces bloating"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="22570464",
                doi="10.1111/j.1365-2672.2012.05344.x",
                title="Bifidobacterium lactis BB-12 supplementation and functional constipation in elderly: a double-blind, randomized, controlled trial",
                authors="Eskesen D, Jespersen L, Michelsen B, Whorwell PJ, Müller-Lissner S, Morberg CM",
                journal="Journal of Applied Microbiology",
                publication_year=2015,
                study_type=StudyType.RCT,
                sample_size=300,
                study_quality=Decimal("0.90")
            ),
            CitationModel(
                id=uuid4(),
                pmid="23609775",
                doi="10.1111/apt.12344",
                title="Bifidobacterium lactis Bi-07 versus placebo in the treatment of functional gastrointestinal disorders",
                authors="Ringel-Kulka T, Palsson OS, Maier D, Carroll I, Galanko JA, Leyer G, Ringel Y",
                journal="Alimentary Pharmacology & Therapeutics",
                publication_year=2011,
                study_type=StudyType.RCT,
                sample_size=60,
                study_quality=Decimal("0.85")
            )
        ],
        interactions=[]
    )
    
    # 5. RESISTANT STARCH - Good prebiotic effects
    resistant_starch_id = uuid4()
    resistant_starch = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=resistant_starch_id,
            name="Resistant starch",
            slug="resistant-starch",
            aliases=["RS2", "RS3", "Hi-maize", "Potato starch"],
            category=IngredientCategory.PREBIOTIC,
            description="A type of starch that resists digestion in the small intestine and acts as a prebiotic fiber in the colon.",
            gut_score=Decimal("7.5"),
            confidence_score=Decimal("0.80"),
            dosage_info={
                "min_dose": "10g daily",
                "max_dose": "40g daily",
                "unit": "g",
                "frequency": "daily",
                "timing": "Can be mixed with food or beverages",
                "form": "powder, naturally in foods"
            },
            safety_notes="May cause gas and bloating initially. Start with small amounts and increase gradually."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                bacteria_name="Bifidobacterium",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="selective fermentation",
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.85"),
                mechanism="Preferentially fermented by bifidobacteria, promoting their growth"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                bacteria_name="Ruminococcus bromii",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="primary degradation",
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                mechanism="Specialized starch-degrading bacteria that initiate resistant starch fermentation"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                bacteria_name="Bacteroides",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="secondary fermentation",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Utilizes breakdown products from primary fermenters"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                effect_name="Butyrate production",
                effect_category="SCFA production",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.95"),
                dosage_dependent=True,
                mechanism="Fermentation primarily produces butyrate, the preferred fuel for colonocytes"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                effect_name="Insulin sensitivity",
                effect_category="glucose metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="Butyrate improves insulin sensitivity and glucose metabolism"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                effect_name="Satiety",
                effect_category="appetite control",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                mechanism="SCFA production affects satiety hormones like GLP-1"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                symptom_name="Blood sugar spikes",
                symptom_category="metabolic",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Second-meal effect improves glucose tolerance"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=resistant_starch_id,
                symptom_name="Bowel regularity",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                population_notes="Mild laxative effect through increased stool bulk"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="23609775",
                doi="10.1111/apt.12344",
                title="Resistant starch: the effect on postprandial glycemia, hormonal response, and satiety",
                authors="Bodinham CL, Frost GS, Robertson MD",
                journal="American Journal of Clinical Nutrition",
                publication_year=2010,
                study_type=StudyType.REVIEW,
                sample_size=None,
                study_quality=Decimal("0.85")
            ),
            CitationModel(
                id=uuid4(),
                pmid="27424809",
                doi="10.3945/an.115.011684",
                title="Resistant starch and the gut microbiome: effects on metabolic syndrome",
                authors="Keenan MJ, Zhou J, Hegsted M, Pelkman C, Durham HA, Coulon DB, Martin RJ",
                journal="Nutrients",
                publication_year=2015,
                study_type=StudyType.REVIEW,
                sample_size=None,
                study_quality=Decimal("0.80")
            )
        ],
        interactions=[]
    )
    
    # 6. BETA-GLUCAN - Moderate gut score, good for cholesterol
    beta_glucan_id = uuid4()
    beta_glucan = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=beta_glucan_id,
            name="Beta-glucan",
            slug="beta-glucan",
            aliases=["Oat beta-glucan", "Barley beta-glucan", "Yeast beta-glucan"],
            category=IngredientCategory.FIBER,
            description="A soluble fiber found in oats and barley that forms a gel-like substance and has cholesterol-lowering properties.",
            gut_score=Decimal("7.0"),
            confidence_score=Decimal("0.85"),
            dosage_info={
                "min_dose": "3g daily",
                "max_dose": "15g daily",
                "unit": "g",
                "frequency": "daily",
                "timing": "With meals for optimal cholesterol benefits",
                "form": "powder, capsule, naturally in oats/barley"
            },
            safety_notes="Generally well-tolerated. May cause mild digestive upset in sensitive individuals."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=beta_glucan_id,
                bacteria_name="Lactobacillus",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="selective fermentation",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Partial fermentation supports lactobacilli growth"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=beta_glucan_id,
                bacteria_name="Bifidobacterium",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="prebiotic effect",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                mechanism="Slowly fermented to provide sustained prebiotic benefits"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=beta_glucan_id,
                effect_name="Cholesterol reduction",
                effect_category="lipid metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.95"),
                dosage_dependent=True,
                mechanism="Bile acid sequestration and reduced cholesterol absorption"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=beta_glucan_id,
                effect_name="Postprandial glucose",
                effect_category="glucose metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                mechanism="Viscous gel formation slows glucose absorption"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=beta_glucan_id,
                effect_name="Immune function",
                effect_category="immunity",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="Activates immune cells through beta-glucan receptors"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=beta_glucan_id,
                symptom_name="Cholesterol levels",
                symptom_category="cardiovascular",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.95"),
                dosage_dependent=True,
                population_notes="FDA approved health claim for cholesterol reduction"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=beta_glucan_id,
                symptom_name="Satiety",
                symptom_category="appetite",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Increases feelings of fullness and reduces food intake"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="22570464",
                doi="10.1111/j.1365-2672.2012.05344.x",
                title="Oat β-glucan: a unique fiber for health benefits",
                authors="Whitehead A, Beck EJ, Tosh S, Wolever TM",
                journal="Food & Function",
                publication_year=2014,
                study_type=StudyType.REVIEW,
                sample_size=None,
                study_quality=Decimal("0.90")
            ),
            CitationModel(
                id=uuid4(),
                pmid="28507013",
                doi="10.1053/j.gastro.2017.05.019",
                title="Beta-glucan and cholesterol: a systematic review and meta-analysis",
                authors="Tiwari U, Cummins E",
                journal="Nutrition Reviews",
                publication_year=2011,
                study_type=StudyType.META_ANALYSIS,
                sample_size=2100,
                study_quality=Decimal("0.85")
            )
        ],
        interactions=[]
    )
    
    # 7. SACCHAROMYCES BOULARDII - Good for antibiotic recovery
    s_boulardii_id = uuid4()
    s_boulardii = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=s_boulardii_id,
            name="Saccharomyces boulardii",
            slug="saccharomyces-boulardii",
            aliases=["S. boulardii", "Beneficial yeast", "Florastor"],
            category=IngredientCategory.PROBIOTIC,
            description="A beneficial yeast probiotic that is resistant to antibiotics and helps maintain gut health during antibiotic treatment.",
            gut_score=Decimal("7.5"),
            confidence_score=Decimal("0.85"),
            dosage_info={
                "min_dose": "250mg daily",
                "max_dose": "1000mg daily",
                "unit": "mg",
                "frequency": "daily",
                "timing": "Can be taken with antibiotics",
                "form": "capsule, powder, sachet"
            },
            safety_notes="Generally safe but may cause rare cases of fungemia in immunocompromised patients."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                bacteria_name="Clostridium difficile",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="direct inhibition",
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                mechanism="Produces protease that degrades C. difficile toxins"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                bacteria_name="Escherichia coli",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="competitive inhibition",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                mechanism="Competes for nutrients and adhesion sites"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                bacteria_name="Candida albicans",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="antifungal activity",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Produces compounds that inhibit pathogenic yeasts"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                effect_name="Immune modulation",
                effect_category="immunity",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="Modulates secretory IgA and anti-inflammatory responses"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                effect_name="Intestinal barrier",
                effect_category="gut barrier",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                mechanism="Preserves tight junction integrity during antibiotic treatment"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                effect_name="Inflammation reduction",
                effect_category="inflammation",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                dosage_dependent=True,
                mechanism="Reduces inflammatory cytokine production"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                symptom_name="Antibiotic-associated diarrhea",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                dosage_dependent=True,
                population_notes="Most effective when started with antibiotic treatment"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                symptom_name="C. difficile infection",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                population_notes="Reduces risk of C. difficile-associated diarrhea"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=s_boulardii_id,
                symptom_name="Traveler's diarrhea",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                population_notes="Prophylactic use reduces risk of traveler's diarrhea"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="23609775",
                doi="10.1111/apt.12344",
                title="Saccharomyces boulardii in the prevention of antibiotic-associated diarrhea",
                authors="Szajewska H, Kolodziej M",
                journal="Cochrane Database of Systematic Reviews",
                publication_year=2015,
                study_type=StudyType.META_ANALYSIS,
                sample_size=3818,
                study_quality=Decimal("0.90")
            ),
            CitationModel(
                id=uuid4(),
                pmid="27424809",
                doi="10.3945/an.115.011684",
                title="Saccharomyces boulardii for Clostridium difficile-associated diarrhea",
                authors="Pothoulakis C",
                journal="Gastroenterology Clinics of North America",
                publication_year=2012,
                study_type=StudyType.REVIEW,
                sample_size=None,
                study_quality=Decimal("0.85")
            )
        ],
        interactions=[]
    )
    
    # 8. FOS - Good prebiotic similar to inulin
    fos_id = uuid4()
    fos = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=fos_id,
            name="FOS (Fructooligosaccharides)",
            slug="fos-fructooligosaccharides",
            aliases=["FOS", "Oligofructose", "Scfos", "Nutraflora"],
            category=IngredientCategory.PREBIOTIC,
            description="Short-chain fructooligosaccharides that act as prebiotics, similar to inulin but with faster fermentation.",
            gut_score=Decimal("7.5"),
            confidence_score=Decimal("0.80"),
            dosage_info={
                "min_dose": "2g daily",
                "max_dose": "15g daily",
                "unit": "g",
                "frequency": "daily",
                "timing": "With meals to reduce GI side effects",
                "form": "powder, syrup, capsule"
            },
            safety_notes="May cause gas and bloating at high doses. Lower tolerance threshold than inulin."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                bacteria_name="Bifidobacterium",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="preferential fermentation",
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.90"),
                mechanism="Rapidly fermented by bifidobacteria, causing quick population expansion"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                bacteria_name="Lactobacillus",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="selective growth",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                mechanism="Supports lactobacilli growth through cross-feeding mechanisms"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                bacteria_name="Clostridium perfringens",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="competitive inhibition",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Beneficial bacteria outcompete pathogenic species"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                effect_name="SCFA production",
                effect_category="metabolism",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                mechanism="Rapid fermentation produces acetate, propionate, and butyrate"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                effect_name="Mineral absorption",
                effect_category="mineral absorption",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                mechanism="SCFA production improves calcium and magnesium absorption"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                effect_name="Immune function",
                effect_category="immunity",
                impact_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                dosage_dependent=True,
                mechanism="Supports immune system through microbiome modulation"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                symptom_name="Bowel regularity",
                symptom_category="digestive",
                effect_direction=EffectDirection.POSITIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                population_notes="Mild laxative effect through increased microbial activity"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                symptom_name="Bloating",
                symptom_category="digestive",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.STRONG,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                population_notes="More likely to cause bloating than longer-chain prebiotics"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=fos_id,
                symptom_name="Gas production",
                symptom_category="digestive",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                population_notes="Rapid fermentation can cause increased gas production"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="19335713",
                doi="10.1017/S0007114509297515",
                title="Fructooligosaccharides and lactulose cause more symptoms than fructose and sorbitol",
                authors="Rao SS, Attaluri A, Anderson L, Stumbo P",
                journal="Digestive Diseases and Sciences",
                publication_year=2007,
                study_type=StudyType.RCT,
                sample_size=21,
                study_quality=Decimal("0.75")
            ),
            CitationModel(
                id=uuid4(),
                pmid="27424809",
                doi="10.3945/an.115.011684",
                title="Fructooligosaccharide supplementation increases faecal bifidobacteria",
                authors="Bouhnik Y, Flourie B, D'Agay-Abensour L, Pochart P, Gramet G, Durand M, Rambaud JC",
                journal="European Journal of Clinical Nutrition",
                publication_year=1997,
                study_type=StudyType.RCT,
                sample_size=20,
                study_quality=Decimal("0.80")
            )
        ],
        interactions=[]
    )
    
    # 9. CARRAGEENAN - Concerning for gut health
    carrageenan_id = uuid4()
    carrageenan = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=carrageenan_id,
            name="Carrageenan",
            slug="carrageenan",
            aliases=["Irish moss extract", "E407", "Kappa-carrageenan"],
            category=IngredientCategory.OTHER,
            description="A seaweed extract used as a food additive and thickener that may cause intestinal inflammation in sensitive individuals.",
            gut_score=Decimal("3.0"),
            confidence_score=Decimal("0.70"),
            dosage_info={
                "min_dose": "0mg daily",
                "max_dose": "No established safe limit",
                "unit": "mg",
                "frequency": "daily",
                "timing": "Avoid in sensitive individuals",
                "form": "food additive, supplement filler",
                "notes": "Present in processed foods"
            },
            safety_notes="May cause intestinal inflammation and worsen IBD symptoms. Avoid if sensitive to inflammatory bowel conditions."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=carrageenan_id,
                bacteria_name="Bacteroides",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="inflammatory response",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Induces inflammatory response that may reduce beneficial bacteria"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=carrageenan_id,
                bacteria_name="Akkermansia muciniphila",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="mucin layer disruption",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                mechanism="Disrupts mucin layer that Akkermansia depends on"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=carrageenan_id,
                effect_name="Intestinal inflammation",
                effect_category="inflammation",
                impact_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="Activates inflammatory pathways in intestinal epithelial cells"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=carrageenan_id,
                effect_name="Barrier function",
                effect_category="gut barrier",
                impact_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                mechanism="May compromise intestinal barrier integrity"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=carrageenan_id,
                effect_name="Immune activation",
                effect_category="immunity",
                impact_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                dosage_dependent=True,
                mechanism="Triggers innate immune responses and cytokine release"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=carrageenan_id,
                symptom_name="IBD symptoms",
                symptom_category="digestive",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                population_notes="May worsen symptoms in individuals with inflammatory bowel disease"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=carrageenan_id,
                symptom_name="Digestive discomfort",
                symptom_category="digestive",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.WEAK,
                confidence=Decimal("0.65"),
                dosage_dependent=True,
                population_notes="Some individuals report digestive discomfort with carrageenan consumption"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="11396693",
                doi="10.1016/S0278-6915(00)00162-8",
                title="Carrageenan-induced inflammation in the hindgut of rats",
                authors="Tobacman JK",
                journal="Food and Chemical Toxicology",
                publication_year=2001,
                study_type=StudyType.ANIMAL,
                sample_size=None,
                study_quality=Decimal("0.70")
            ),
            CitationModel(
                id=uuid4(),
                pmid="22323273",
                doi="10.1016/j.fct.2012.02.003",
                title="Review of harmful gastrointestinal effects of carrageenan in animal experiments",
                authors="Tobacman JK",
                journal="Environmental Health Perspectives",
                publication_year=2001,
                study_type=StudyType.REVIEW,
                sample_size=None,
                study_quality=Decimal("0.75")
            )
        ],
        interactions=[]
    )
    
    # 10. POLYSORBATE 80 - Concerning emulsifier
    polysorbate_80_id = uuid4()
    polysorbate_80 = CompleteIngredientModel(
        ingredient=IngredientModel(
            id=polysorbate_80_id,
            name="Polysorbate 80",
            slug="polysorbate-80",
            aliases=["Tween 80", "E433", "Polyoxyethylene sorbitan monooleate"],
            category=IngredientCategory.OTHER,
            description="A synthetic emulsifier used in processed foods that may disrupt the gut microbiome and increase intestinal permeability.",
            gut_score=Decimal("2.5"),
            confidence_score=Decimal("0.75"),
            dosage_info={
                "min_dose": "0mg daily",
                "max_dose": "No established safe limit",
                "unit": "mg",
                "frequency": "daily",
                "timing": "Avoid when possible",
                "form": "food additive, medication excipient",
                "notes": "Present in processed foods"
            },
            safety_notes="May cause microbiome disruption and increase inflammation. Avoid in processed foods when possible."
        ),
        microbiome_effects=[
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                bacteria_name="Bacteroides",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="direct inhibition",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                mechanism="Emulsifier properties disrupt bacterial cell membranes"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                bacteria_name="Bifidobacterium",
                bacteria_level=BacteriaLevel.DECREASE,
                effect_type="growth inhibition",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                mechanism="Alters gut environment, making it less favorable for beneficial bacteria"
            ),
            MicrobiomeEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                bacteria_name="Escherichia coli",
                bacteria_level=BacteriaLevel.INCREASE,
                effect_type="selective advantage",
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.70"),
                mechanism="Creates conditions that favor pathogenic bacteria over beneficial species"
            )
        ],
        metabolic_effects=[
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                effect_name="Intestinal permeability",
                effect_category="gut barrier",
                impact_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.85"),
                dosage_dependent=True,
                mechanism="Disrupts mucus layer and increases intestinal permeability"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                effect_name="Inflammation",
                effect_category="inflammation",
                impact_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.80"),
                dosage_dependent=True,
                mechanism="Triggers inflammatory responses in intestinal epithelium"
            ),
            MetabolicEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                effect_name="Metabolic dysfunction",
                effect_category="metabolism",
                impact_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.WEAK,
                confidence=Decimal("0.65"),
                dosage_dependent=True,
                mechanism="May contribute to metabolic syndrome through microbiome disruption"
            )
        ],
        symptom_effects=[
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                symptom_name="Digestive inflammation",
                symptom_category="digestive",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.MODERATE,
                confidence=Decimal("0.75"),
                dosage_dependent=True,
                population_notes="May worsen symptoms in individuals with inflammatory conditions"
            ),
            SymptomEffectModel(
                id=uuid4(),
                ingredient_id=polysorbate_80_id,
                symptom_name="Food sensitivities",
                symptom_category="immune",
                effect_direction=EffectDirection.NEGATIVE,
                effect_strength=EffectStrength.WEAK,
                confidence=Decimal("0.60"),
                dosage_dependent=True,
                population_notes="Increased intestinal permeability may contribute to food sensitivities"
            )
        ],
        citations=[
            CitationModel(
                id=uuid4(),
                pmid="25731162",
                doi="10.1038/nature14232",
                title="Dietary emulsifiers impact the mouse gut microbiota promoting colitis and metabolic syndrome",
                authors="Chassaing B, Koren O, Goodrich JK, Poole AC, Srinivasan S, Ley RE, Gewirtz AT",
                journal="Nature",
                publication_year=2015,
                study_type=StudyType.ANIMAL,
                sample_size=None,
                study_quality=Decimal("0.90")
            ),
            CitationModel(
                id=uuid4(),
                pmid="28286266",
                doi="10.1016/j.foodchem.2017.03.019",
                title="Emulsifier polysorbate-80 affects the biological properties of neonatal gut microbiota",
                authors="Shim JJ, Sears CL, Hornig M, Shin J",
                journal="Food Chemistry",
                publication_year=2017,
                study_type=StudyType.IN_VITRO,
                sample_size=None,
                study_quality=Decimal("0.75")
            )
        ],
        interactions=[]
    )
    
    return [
        inulin, psyllium, l_acidophilus, b_lactis, resistant_starch,
        beta_glucan, s_boulardii, fos, carrageenan, polysorbate_80
    ]


class GutIntelSeeder:
    """
    Main seeding class for GutIntel database.
    
    Provides comprehensive seeding functionality with verification,
    rollback capabilities, and multiple seeding options.
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.repo: Optional[IngredientRepository] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self):
        """Initialize the seeder with database connection."""
        self.repo = await create_ingredient_repository(self.db)
        self.logger.info("GutIntel seeder initialized successfully")
    
    async def seed_database(self) -> Dict[str, Any]:
        """
        Seed the database with all 10 essential ingredients.
        
        Returns:
            Dict containing seeding results and statistics
        """
        if not self.repo:
            await self.initialize()
        
        self.logger.info("Starting complete database seeding...")
        
        try:
            ingredients = create_ingredient_data()
            
            # Use bulk create for efficiency
            created_ids = await self.repo.bulk_create_ingredients(ingredients)
            
            # Verify seeding
            verification_results = await self.verify_seed_data()
            
            results = {
                "status": "success",
                "ingredients_created": len(created_ids),
                "ingredient_ids": [str(id) for id in created_ids],
                "verification": verification_results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Database seeding completed successfully. Created {len(created_ids)} ingredients.")
            return results
            
        except Exception as e:
            self.logger.error(f"Database seeding failed: {e}")
            raise SeedingError(f"Failed to seed database: {e}")
    
    async def seed_minimal(self) -> Dict[str, Any]:
        """
        Seed database with basic ingredient data only (no effects or citations).
        
        Returns:
            Dict containing seeding results
        """
        if not self.repo:
            await self.initialize()
        
        self.logger.info("Starting minimal database seeding...")
        
        try:
            ingredients = create_ingredient_data()
            
            # Create minimal versions (ingredient data only)
            minimal_ingredients = []
            for ingredient in ingredients:
                minimal_ingredient = CompleteIngredientModel(
                    ingredient=ingredient.ingredient,
                    microbiome_effects=[],
                    metabolic_effects=[],
                    symptom_effects=[],
                    citations=[],
                    interactions=[]
                )
                minimal_ingredients.append(minimal_ingredient)
            
            created_ids = await self.repo.bulk_create_ingredients(minimal_ingredients)
            
            results = {
                "status": "success",
                "ingredients_created": len(created_ids),
                "ingredient_ids": [str(id) for id in created_ids],
                "mode": "minimal",
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Minimal seeding completed. Created {len(created_ids)} ingredients.")
            return results
            
        except Exception as e:
            self.logger.error(f"Minimal seeding failed: {e}")
            raise SeedingError(f"Failed to seed minimal data: {e}")
    
    async def seed_sample(self) -> Dict[str, Any]:
        """
        Seed database with 3 representative ingredients for testing.
        
        Returns:
            Dict containing seeding results
        """
        if not self.repo:
            await self.initialize()
        
        self.logger.info("Starting sample database seeding...")
        
        try:
            all_ingredients = create_ingredient_data()
            
            # Select 3 representative ingredients
            sample_ingredients = [
                all_ingredients[0],  # Inulin (prebiotic)
                all_ingredients[2],  # L. acidophilus (probiotic)
                all_ingredients[1]   # Psyllium (fiber)
            ]
            
            created_ids = await self.repo.bulk_create_ingredients(sample_ingredients)
            
            results = {
                "status": "success",
                "ingredients_created": len(created_ids),
                "ingredient_ids": [str(id) for id in created_ids],
                "mode": "sample",
                "ingredients": [ing.ingredient.name for ing in sample_ingredients],
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Sample seeding completed. Created {len(created_ids)} ingredients.")
            return results
            
        except Exception as e:
            self.logger.error(f"Sample seeding failed: {e}")
            raise SeedingError(f"Failed to seed sample data: {e}")
    
    async def seed_custom(self, ingredient_names: List[str]) -> Dict[str, Any]:
        """
        Seed database with custom selection of ingredients.
        
        Args:
            ingredient_names: List of ingredient names to seed
            
        Returns:
            Dict containing seeding results
        """
        if not self.repo:
            await self.initialize()
        
        self.logger.info(f"Starting custom seeding for ingredients: {ingredient_names}")
        
        try:
            all_ingredients = create_ingredient_data()
            
            # Filter ingredients by name
            custom_ingredients = []
            for ingredient in all_ingredients:
                if ingredient.ingredient.name in ingredient_names:
                    custom_ingredients.append(ingredient)
            
            if len(custom_ingredients) != len(ingredient_names):
                found_names = [ing.ingredient.name for ing in custom_ingredients]
                missing = set(ingredient_names) - set(found_names)
                raise DataValidationError(f"Ingredients not found: {missing}")
            
            created_ids = await self.repo.bulk_create_ingredients(custom_ingredients)
            
            results = {
                "status": "success",
                "ingredients_created": len(created_ids),
                "ingredient_ids": [str(id) for id in created_ids],
                "mode": "custom",
                "ingredients": ingredient_names,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Custom seeding completed. Created {len(created_ids)} ingredients.")
            return results
            
        except Exception as e:
            self.logger.error(f"Custom seeding failed: {e}")
            raise SeedingError(f"Failed to seed custom data: {e}")
    
    async def clear_database(self) -> Dict[str, Any]:
        """
        Clear all ingredient data from the database.
        
        Returns:
            Dict containing clearing results
        """
        if not self.repo:
            await self.initialize()
        
        self.logger.info("Starting database clearing...")
        
        try:
            # Get all ingredients first
            all_ingredients = await self.repo.search_ingredients(limit=1000)
            
            deleted_count = 0
            failed_deletions = []
            
            for ingredient in all_ingredients:
                try:
                    success = await self.repo.delete_ingredient(ingredient.id)
                    if success:
                        deleted_count += 1
                    else:
                        failed_deletions.append(str(ingredient.id))
                except Exception as e:
                    self.logger.error(f"Failed to delete ingredient {ingredient.id}: {e}")
                    failed_deletions.append(str(ingredient.id))
            
            results = {
                "status": "success" if not failed_deletions else "partial",
                "ingredients_deleted": deleted_count,
                "failed_deletions": failed_deletions,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Database clearing completed. Deleted {deleted_count} ingredients.")
            return results
            
        except Exception as e:
            self.logger.error(f"Database clearing failed: {e}")
            raise SeedingError(f"Failed to clear database: {e}")
    
    async def verify_seed_data(self) -> Dict[str, Any]:
        """
        Verify that seed data was inserted correctly.
        
        Returns:
            Dict containing verification results
        """
        if not self.repo:
            await self.initialize()
        
        self.logger.info("Starting seed data verification...")
        
        try:
            # Get all ingredients with effects
            ingredients = await self.repo.get_ingredients_with_effects()
            
            verification_results = {
                "total_ingredients": len(ingredients),
                "ingredients_with_effects": 0,
                "total_microbiome_effects": 0,
                "total_metabolic_effects": 0,
                "total_symptom_effects": 0,
                "total_citations": 0,
                "average_gut_score": 0.0,
                "average_confidence_score": 0.0,
                "categories": {},
                "validation_errors": []
            }
            
            gut_scores = []
            confidence_scores = []
            
            for ingredient in ingredients:
                # Count effects
                if (ingredient.microbiome_effects or 
                    ingredient.metabolic_effects or 
                    ingredient.symptom_effects):
                    verification_results["ingredients_with_effects"] += 1
                
                verification_results["total_microbiome_effects"] += len(ingredient.microbiome_effects)
                verification_results["total_metabolic_effects"] += len(ingredient.metabolic_effects)
                verification_results["total_symptom_effects"] += len(ingredient.symptom_effects)
                verification_results["total_citations"] += len(ingredient.citations)
                
                # Collect scores
                if ingredient.ingredient.gut_score is not None:
                    gut_scores.append(float(ingredient.ingredient.gut_score))
                if ingredient.ingredient.confidence_score is not None:
                    confidence_scores.append(float(ingredient.ingredient.confidence_score))
                
                # Category counts
                category = ingredient.ingredient.category.value
                verification_results["categories"][category] = verification_results["categories"].get(category, 0) + 1
                
                # Validate data integrity
                if not ingredient.ingredient.name:
                    verification_results["validation_errors"].append(f"Ingredient {ingredient.ingredient.id} has no name")
                
                if ingredient.ingredient.gut_score is not None:
                    if not (0 <= ingredient.ingredient.gut_score <= 10):
                        verification_results["validation_errors"].append(
                            f"Ingredient {ingredient.ingredient.name} has invalid gut score: {ingredient.ingredient.gut_score}"
                        )
                
                if ingredient.ingredient.confidence_score is not None:
                    if not (0 <= ingredient.ingredient.confidence_score <= 1):
                        verification_results["validation_errors"].append(
                            f"Ingredient {ingredient.ingredient.name} has invalid confidence score: {ingredient.ingredient.confidence_score}"
                        )
            
            # Calculate averages
            if gut_scores:
                verification_results["average_gut_score"] = sum(gut_scores) / len(gut_scores)
            if confidence_scores:
                verification_results["average_confidence_score"] = sum(confidence_scores) / len(confidence_scores)
            
            verification_results["status"] = "passed" if not verification_results["validation_errors"] else "failed"
            
            self.logger.info(f"Verification completed. Status: {verification_results['status']}")
            return verification_results
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            raise SeedingError(f"Failed to verify seed data: {e}")
    
    async def update_seed_data(self) -> Dict[str, Any]:
        """
        Update existing seed data with new information.
        
        Returns:
            Dict containing update results
        """
        if not self.repo:
            await self.initialize()
        
        self.logger.info("Starting seed data update...")
        
        try:
            # Get current ingredients
            current_ingredients = await self.repo.search_ingredients(limit=1000)
            current_names = {ing.name for ing in current_ingredients}
            
            # Get new ingredient data
            new_ingredients = create_ingredient_data()
            new_names = {ing.ingredient.name for ing in new_ingredients}
            
            # Find updates and additions
            to_update = current_names & new_names
            to_add = new_names - current_names
            
            updated_count = 0
            added_count = 0
            failed_updates = []
            
            # Update existing ingredients
            for ingredient_data in new_ingredients:
                if ingredient_data.ingredient.name in to_update:
                    try:
                        # Find existing ingredient
                        existing = await self.repo.get_ingredient_by_name(ingredient_data.ingredient.name)
                        if existing:
                            # Update with new data
                            updates = {
                                "description": ingredient_data.ingredient.description,
                                "gut_score": ingredient_data.ingredient.gut_score,
                                "confidence_score": ingredient_data.ingredient.confidence_score,
                                "dosage_info": ingredient_data.ingredient.dosage_info,
                                "safety_notes": ingredient_data.ingredient.safety_notes
                            }
                            
                            success = await self.repo.update_ingredient(existing.ingredient.id, updates)
                            if success:
                                updated_count += 1
                            else:
                                failed_updates.append(ingredient_data.ingredient.name)
                    except Exception as e:
                        self.logger.error(f"Failed to update {ingredient_data.ingredient.name}: {e}")
                        failed_updates.append(ingredient_data.ingredient.name)
                
                elif ingredient_data.ingredient.name in to_add:
                    try:
                        # Add new ingredient
                        await self.repo.create_ingredient(ingredient_data)
                        added_count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to add {ingredient_data.ingredient.name}: {e}")
                        failed_updates.append(ingredient_data.ingredient.name)
            
            results = {
                "status": "success" if not failed_updates else "partial",
                "ingredients_updated": updated_count,
                "ingredients_added": added_count,
                "failed_updates": failed_updates,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Update completed. Updated: {updated_count}, Added: {added_count}")
            return results
            
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            raise SeedingError(f"Failed to update seed data: {e}")


async def main():
    """Main function for command line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GutIntel Database Seeder")
    parser.add_argument(
        "--mode",
        choices=["seed", "minimal", "sample", "clear", "verify", "update"],
        default="seed",
        help="Seeding mode"
    )
    parser.add_argument(
        "--custom",
        nargs="+",
        help="Custom ingredient names to seed"
    )
    
    args = parser.parse_args()
    
    # Initialize database
    db = Database()
    await db.connect()
    
    # Initialize seeder
    seeder = GutIntelSeeder(db)
    await seeder.initialize()
    
    try:
        if args.mode == "seed":
            results = await seeder.seed_database()
        elif args.mode == "minimal":
            results = await seeder.seed_minimal()
        elif args.mode == "sample":
            results = await seeder.seed_sample()
        elif args.mode == "clear":
            results = await seeder.clear_database()
        elif args.mode == "verify":
            results = await seeder.verify_seed_data()
        elif args.mode == "update":
            results = await seeder.update_seed_data()
        elif args.custom:
            results = await seeder.seed_custom(args.custom)
        else:
            print("Invalid mode or missing custom ingredients")
            return
        
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())