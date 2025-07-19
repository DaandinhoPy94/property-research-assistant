# api/ai_analyzer.py
import google.generativeai as genai
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PropertyAIAnalyzer:
    """
    AI-powered property analysis using Google Gemini
    """
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCWGXqSnxZy5qME72qU4XQVYDxUfe8Mvk8")
        genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    
    async def generate_comprehensive_analysis(
        self, 
        property_data: Dict,
        market_analysis: Dict
    ) -> Dict:
        """
        Generate comprehensive AI analysis of property investment potential
        """
        try:
            # Prepare structured data for AI analysis
            analysis_prompt = self._build_analysis_prompt(property_data, market_analysis)
            
            print(f"🤖 Sending analysis request to Gemini...")
            
            # Call Gemini API
            response = self.model.generate_content(
                analysis_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            # Parse AI response - extract JSON from response
            response_text = response.text
            
            # Try to extract JSON from the response
            try:
                # Look for JSON block in response
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif "{" in response_text and "}" in response_text:
                    # Find first { and last }
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    json_text = response_text[json_start:json_end]
                else:
                    raise ValueError("No JSON found in response")
                
                ai_analysis = json.loads(json_text)
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ JSON parsing failed: {e}")
                print(f"Raw response: {response_text[:200]}...")
                # Return fallback analysis
                return self._generate_fallback_analysis(property_data, market_analysis)
            
            print(f"✅ Gemini analysis completed")
            
            # Add metadata
            ai_analysis["ai_metadata"] = {
                "model_used": "gemini-1.5-flash",
                "tokens_used": "estimated",
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence_score": self._calculate_confidence_score(ai_analysis)
            }
            
            return ai_analysis
            
        except Exception as e:
            print(f"❌ Gemini analysis failed: {str(e)}")
            # Return fallback analysis
            return self._generate_fallback_analysis(property_data, market_analysis)
    
    def _get_system_prompt(self) -> str:
        """
        System prompt that defines the AI's role and expertise
        """
        return """Je bent een senior vastgoed investment analist met 15+ jaar ervaring in de Nederlandse markt. 

Je expertise omvat:
- Vastgoedwaardering en marktanalyse
- Investeringsrisico's en rendementsprognoses  
- Nederlandse vastgoedmarkt trends
- Locatieanalyse en demografische factoren
- ROI berekeningen en cashflow modelling

Je analyseert properties objectief en geeft praktische investment adviezen. Je responses zijn altijd in het Nederlands en in JSON format.

Analyseer elke property op:
1. Investeringspotentieel (korte en lange termijn)
2. Risicofactoren en mitigation strategieën
3. Marktpositie en concurrentie-analyse
4. Specifieke action items voor de investeerder
5. Voorspelling van waardeontwikkeling

Blijf professioneel maar toegankelijk in je toon."""

    def _build_analysis_prompt(self, property_data: Dict, market_analysis: Dict) -> str:
        """
        Build detailed analysis prompt with all available data
        """
        return f"""
Je bent een senior vastgoed investment analist met 15+ jaar ervaring in de Nederlandse markt. 

Analyseer deze Nederlandse vastgoedinvestering en genereer een comprehensive report.

PROPERTY DETAILS:
- Adres: {property_data.get('address')}, {property_data.get('city')}
- Type: {property_data.get('property_type')}
- Grootte: {property_data.get('size_m2')}m²
- Vraagprijs: €{property_data.get('asking_price'):,.0f}
- Prijs per m²: €{property_data.get('asking_price', 0) / property_data.get('size_m2', 1):,.0f}

MARKT ANALYSE DATA:
- Market Score: {market_analysis.get('market_score', 0)}/100
- Prijs vs Markt: {market_analysis.get('price_analysis', {}).get('price_difference_pct', 0):+.1f}%
- Locatie Score: {market_analysis.get('location_analysis', {}).get('location_score', 0)}/10
- Gemiddeld Inkomen Buurt: €{market_analysis.get('demographic_insights', {}).get('average_income', 0):,}
- Bevolkingsgroei: {market_analysis.get('demographic_insights', {}).get('population_growth', 0)}%
- Werkgelegenheid: {market_analysis.get('demographic_insights', {}).get('employment_rate', 0)}%

LOCATIE STERKE PUNTEN:
{chr(10).join('- ' + strength for strength in market_analysis.get('location_analysis', {}).get('strengths', []))}

AANDACHTSPUNTEN:
{chr(10).join('- ' + weakness for weakness in market_analysis.get('location_analysis', {}).get('weaknesses', []))}

VERGELIJKBARE VERKOPEN (laatste 6 maanden):
{chr(10).join(f"- {comp.get('address', 'Unknown')}: €{comp.get('sold_price', 0):,.0f} ({comp.get('size_m2', 0):.0f}m²)" for comp in market_analysis.get('comparable_properties', [])[:3])}

Genereer een JSON response met exact deze structuur:

```json
{{
    "executive_summary": "Beknopte samenvatting van 2-3 zinnen over de investeringskans",
    "investment_grade": "A+/A/A-/B+/B/B-/C+/C/C-/D",
    "key_insights": [
        "3-5 belangrijkste bevindingen als bullet points",
        "Focus op unieke aspects van deze property/locatie"
    ],
    "financial_analysis": {{
        "value_assessment": "Undervalued/Fair Value/Overvalued + toelichting",
        "rental_yield_estimate": "X.X% - geschatte bruto huurrendement",
        "appreciation_forecast": "Conservative/Moderate/Strong + 5-jaar voorspelling",
        "total_return_projection": "X-X% verwacht jaarlijks totaalrendement"
    }},
    "risk_assessment": {{
        "risk_level": "Low/Medium/High",
        "primary_risks": [
            "Top 2-3 risicofactoren specifiek voor deze property"
        ],
        "risk_mitigation": [
            "Concrete stappen om risico's te verminderen"
        ]
    }},
    "market_positioning": {{
        "competitive_advantage": "Wat maakt deze property uniek/aantrekkelijk",
        "target_tenant_profile": "Beschrijving ideale huurder/koper",
        "market_timing": "Excellent/Good/Neutral/Poor + timing rationale"
    }},
    "action_recommendations": [
        "3-5 concrete next steps voor de investeerder",
        "Inclusief urgentie en prioriteit"
    ],
    "bottom_line": "KOPEN/OVERWEGEN/AFWACHTEN + kernreden in 1 zin"
}}
```

Zorg dat alle percentages realistisch zijn voor de Nederlandse markt 2024-2025.
"""

    def _calculate_confidence_score(self, ai_analysis: Dict) -> float:
        """
        Calculate confidence score based on analysis completeness and data quality
        """
        score = 0.5  # Base score
        
        # Check completeness of analysis
        required_fields = [
            "executive_summary", "investment_grade", "key_insights",
            "financial_analysis", "risk_assessment", "action_recommendations"
        ]
        
        for field in required_fields:
            if field in ai_analysis and ai_analysis[field]:
                score += 0.08
        
        # Bonus for detailed insights
        if len(ai_analysis.get("key_insights", [])) >= 3:
            score += 0.1
        if len(ai_analysis.get("action_recommendations", [])) >= 3:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_fallback_analysis(self, property_data: Dict, market_analysis: Dict) -> Dict:
        """
        Generate basic analysis when OpenAI fails
        """
        market_score = market_analysis.get('market_score', 50)
        price_diff = market_analysis.get('price_analysis', {}).get('price_difference_pct', 0)
        
        # Determine grade based on market score
        if market_score >= 85:
            grade = "A"
        elif market_score >= 75:
            grade = "B+"
        elif market_score >= 65:
            grade = "B"
        elif market_score >= 55:
            grade = "B-"
        else:
            grade = "C"
        
        return {
            "executive_summary": f"Property in {property_data.get('city')} met market score van {market_score:.1f}/100. {'Aantrekkelijke' if market_score > 70 else 'Gemiddelde'} investeringskans.",
            "investment_grade": grade,
            "key_insights": [
                f"Market score: {market_score:.1f}/100",
                f"Prijs {'boven' if price_diff > 0 else 'onder'} marktgemiddelde: {abs(price_diff):.1f}%",
                f"Locatie in {property_data.get('city')} - {'sterke' if market_score > 70 else 'gemiddelde'} markt"
            ],
            "financial_analysis": {
                "value_assessment": "Fair Value - gebaseerd op vergelijkbare verkopen",
                "rental_yield_estimate": "4.5% - schatting bruto huurrendement",
                "appreciation_forecast": "Moderate - in lijn met marktgemiddelde",
                "total_return_projection": "6-8% verwacht jaarlijks totaalrendement"
            },
            "risk_assessment": {
                "risk_level": "Medium",
                "primary_risks": ["Marktvolatiliteit", "Locatie-specifieke factoren"],
                "risk_mitigation": ["Grondige due diligence", "Professionele taxatie"]
            },
            "market_positioning": {
                "competitive_advantage": "Standaard marktpositie",
                "target_tenant_profile": "Lokale huurders en kopers",
                "market_timing": "Neutral - stabiele marktomstandigheden"
            },
            "action_recommendations": [
                "Vraag professionele taxatie aan",
                "Onderzoek vergelijkbare properties in de buurt",
                "Controleer technische staat van het pand"
            ],
            "bottom_line": "OVERWEGEN - Verdient nader onderzoek",
            "ai_metadata": {
                "model_used": "fallback_analysis",
                "tokens_used": 0,
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence_score": 0.6
            }
        }

    async def generate_market_insights(
        self, 
        city: str, 
        market_data: Dict
    ) -> Dict:
        """
        Generate broader market insights for a specific city/region
        """
        try:
            prompt = f"""
Analyseer de vastgoedmarkt voor {city} op basis van deze data:

MARKTDATA:
- Gemiddeld inkomen: €{market_data.get('average_income', 0):,}
- Bevolkingsgroei: {market_data.get('population_growth', 0)}%
- Werkgelegenheid: {market_data.get('employment_rate', 0)}%
- Criminaliteitscijfer: {market_data.get('crime_index', 0)}/10

Genereer markt insights in JSON format:

```json
{{
    "market_outlook": "Positive/Neutral/Negative + korte toelichting",
    "growth_drivers": ["Top 3 factoren die groei stimuleren"],
    "market_challenges": ["Top 2-3 uitdagingen voor de markt"],
    "investment_timing": "Excellent/Good/Neutral/Poor voor nieuwe investeringen",
    "price_trend_forecast": "Stijgend/Stabiel/Dalend voor komende 12 maanden",
    "recommended_strategy": "Specifiek advies voor investeerders in {city}"
}}
```
"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.6,
                )
            )
            
            response_text = response.text
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                raise ValueError("No JSON found")
            
            return json.loads(json_text)
            
        except Exception as e:
            print(f"❌ Market insights generation failed: {str(e)}")
            return {
                "market_outlook": "Neutral - beperkte data beschikbaar",
                "growth_drivers": ["Economische stabiliteit", "Locatie voordelen"],
                "market_challenges": ["Marktvolatiliteit", "Regelgeving wijzigingen"],
                "investment_timing": "Neutral",
                "price_trend_forecast": "Stabiel",
                "recommended_strategy": f"Voorzichtige benadering voor investeringen in {city}"
            }

# Create global instance
ai_analyzer = PropertyAIAnalyzer()