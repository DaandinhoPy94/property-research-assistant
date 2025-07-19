# api/property_research_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Property Research API",
    description="Automated property research and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models for request/response
class PropertyRequest(BaseModel):
    address: str = Field(..., description="Property address")
    city: str = Field(..., description="City name")
    postal_code: str = Field(..., description="Postal code (1234AB format)")
    property_type: str = Field(..., description="Type of property (house/apartment)")
    size_m2: float = Field(..., gt=0, description="Size in square meters")
    asking_price: float = Field(..., gt=0, description="Asking price in euros")
    email_notification: Optional[str] = Field(None, description="Email for notifications")

class LocationAnalysis(BaseModel):
    market_score: float = Field(..., description="Market score (0-100)")
    price_analysis: Dict = Field(..., description="Price comparison data")
    location_analysis: Dict = Field(..., description="Location quality metrics")
    demographic_insights: Dict = Field(..., description="Demographic data")
    comparable_properties: List[Dict] = Field(..., description="Comparable sales")
    investment_recommendation: str = Field(..., description="Investment advice")
    ai_analysis: Optional[Dict] = Field(None, description="AI-powered comprehensive analysis")
    market_insights: Optional[Dict] = Field(None, description="Broader market insights")

class AnalysisResponse(BaseModel):
    status: str
    property_id: Optional[str] = None
    analysis: LocationAnalysis
    timestamp: str
    processing_time_seconds: float

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Property Research API is running",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "analyze": "/analyze_location",
            "webhook": "/webhook/property_added"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "Available",
        "api_version": "1.0.0"
    }

# Main analysis endpoint
@app.post("/analyze_location", response_model=AnalysisResponse)
async def analyze_location(property: PropertyRequest):
    """
    Analyze a property location and generate comprehensive research report
    """
    start_time = datetime.now()
    
    try:
        print(f"🔍 Starting analysis for {property.address}, {property.city}")
        
        # Step 1: Get CBS neighborhood data
        print("📊 Fetching CBS data...")
        cbs_data = await get_cbs_neighborhood_data(property.postal_code, property.city)
        
        # Step 2: Get demographic data
        print("👥 Analyzing demographics...")
        demographics = await get_demographics(property.city, property.postal_code)
        
        # Step 3: Find comparable properties
        print("🏠 Finding comparable properties...")
        comparables = await find_comparable_properties(property)
        
        # Step 4: Calculate market score and analysis
        print("📈 Calculating market analysis...")
        market_analysis = calculate_market_score(
            property,
            cbs_data,
            demographics,
            comparables
        )
        
        # Step 5: Generate AI-powered analysis
        print("🤖 Generating AI analysis...")
        try:
            # Import AI analyzer here to avoid import issues
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from ai_analyzer import ai_analyzer
            
            ai_analysis = await ai_analyzer.generate_comprehensive_analysis(
                property.dict(),
                market_analysis
            )
            print(f"✅ AI Analysis received: {type(ai_analysis)}")
        except Exception as ai_error:
            print(f"❌ AI Analysis failed: {str(ai_error)}")
            ai_analysis = {"error": str(ai_error), "fallback": True}
        
        # Step 6: Generate broader market insights
        print("🌍 Generating market insights...")
        try:
            market_insights = await ai_analyzer.generate_market_insights(
                property.city,
                cbs_data
            )
            print(f"✅ Market Insights received: {type(market_insights)}")
        except Exception as market_error:
            print(f"❌ Market Insights failed: {str(market_error)}")
            market_insights = {"error": str(market_error), "fallback": True}
        
        # Add AI analysis to market analysis
        market_analysis["ai_analysis"] = ai_analysis
        market_analysis["market_insights"] = market_insights
        
        # Step 7: Generate analysis response
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = AnalysisResponse(
            status="success",
            analysis=LocationAnalysis(**market_analysis),
            timestamp=datetime.now().isoformat(),
            processing_time_seconds=round(processing_time, 2)
        )
        
        print(f"✅ Analysis completed in {processing_time:.2f} seconds")
        return response
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

# Webhook endpoint for Make.com integration
@app.post("/webhook/property_added")
async def handle_new_property(data: Dict):
    """
    Webhook endpoint for Make.com automation
    Receives property data and triggers analysis
    """
    try:
        # Convert incoming webhook data to PropertyRequest
        property_req = PropertyRequest(
            address=data.get("address", ""),
            city=data.get("city", ""),
            postal_code=data.get("postal_code", ""),
            property_type=data.get("property_type", "house"),
            size_m2=float(data.get("size_m2", 100)),
            asking_price=float(data.get("asking_price", 300000)),
            email_notification=data.get("email", None)
        )
        
        # Run analysis
        analysis_result = await analyze_location(property_req)
        
        # Return webhook-friendly response
        return {
            "status": "success",
            "property_id": data.get("id"),
            "webhook_received": True,
            "analysis": analysis_result.analysis.dict(),
            "timestamp": datetime.now().isoformat(),
            "next_steps": [
                "Generate report",
                "Send notifications",
                "Update spreadsheet"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Helper functions for data collection and analysis
async def get_cbs_neighborhood_data(postal_code: str, city: str):
    """
    Get CBS neighborhood data - for now simulated, later integrate with real API
    """
    # In production: integrate with CBS API like in Project 1
    # For now, return realistic simulation based on city
    
    city_data_map = {
        "Amsterdam": {
            "average_income": 52000,
            "population_density": 4500,
            "crime_index": 4.1,
            "green_space_percentage": 20,
            "avg_house_value": 520000,
            "growth_rate": 3.2
        },
        "Rotterdam": {
            "average_income": 45000,
            "population_density": 3200,
            "crime_index": 3.8,
            "green_space_percentage": 15,
            "avg_house_value": 380000,
            "growth_rate": 2.8
        },
        "Utrecht": {
            "average_income": 48000,
            "population_density": 3800,
            "crime_index": 2.9,
            "green_space_percentage": 25,
            "avg_house_value": 450000,
            "growth_rate": 4.1
        }
    }
    
    # Default data if city not in map
    default_data = {
        "average_income": 42000,
        "population_density": 2800,
        "crime_index": 3.5,
        "green_space_percentage": 18,
        "avg_house_value": 350000,
        "growth_rate": 2.5
    }
    
    base_data = city_data_map.get(city, default_data)
    
    # Add detailed demographics
    base_data["demographics"] = {
        "age_0_15": 18,
        "age_15_25": 12,
        "age_25_45": 35,
        "age_45_65": 25,
        "age_65_plus": 10
    }
    
    return base_data

async def get_demographics(city: str, postal_code: str):
    """
    Get detailed demographic and facility data
    """
    # Simulate demographic data based on city type
    major_cities = ["Amsterdam", "Rotterdam", "Utrecht", "Den Haag", "Eindhoven"]
    
    if city in major_cities:
        return {
            "population_growth": 2.8,
            "employment_rate": 94.5,
            "avg_household_size": 2.2,
            "education_level": {
                "high": 55,
                "medium": 30,
                "low": 15
            },
            "facilities_nearby": {
                "schools": 8,
                "supermarkets": 6,
                "public_transport": 9,
                "healthcare": 4,
                "restaurants": 25,
                "parks": 3
            },
            "commute_time_amsterdam": 25 if city != "Amsterdam" else 0
        }
    else:
        return {
            "population_growth": 1.2,
            "employment_rate": 91.8,
            "avg_household_size": 2.6,
            "education_level": {
                "high": 35,
                "medium": 40,
                "low": 25
            },
            "facilities_nearby": {
                "schools": 3,
                "supermarkets": 2,
                "public_transport": 5,
                "healthcare": 1,
                "restaurants": 8,
                "parks": 2
            },
            "commute_time_amsterdam": 45
        }

async def find_comparable_properties(property: PropertyRequest):
    """
    Find comparable sold properties (simulated for now)
    """
    import random
    
    comparables = []
    
    # Generate 5 realistic comparable properties
    for i in range(5):
        # Vary price by ±15%
        price_variation = random.uniform(0.85, 1.15)
        comp_price = property.asking_price * price_variation
        
        # Vary size by ±20%
        size_variation = random.uniform(0.8, 1.2)
        comp_size = property.size_m2 * size_variation
        
        comp = {
            "address": f"{property.city} Comparable {i+1}",
            "sold_price": round(comp_price, -3),  # Round to nearest 1000
            "sold_date": f"2024-0{random.randint(1,9)}-{random.randint(10,28)}",
            "size_m2": round(comp_size, 0),
            "price_per_m2": round(comp_price / comp_size, 0),
            "days_on_market": random.randint(15, 90),
            "property_type": property.property_type
        }
        comparables.append(comp)
    
    return comparables

def calculate_market_score(property, cbs_data, demographics, comparables):
    """
    Calculate comprehensive market score and analysis
    """
    # Price analysis
    avg_comp_price = sum(c["sold_price"] for c in comparables) / len(comparables)
    price_delta = (property.asking_price - avg_comp_price) / avg_comp_price * 100
    
    # Location score calculation (0-10 scale)
    income_score = min(10, cbs_data["average_income"] / 5000)
    safety_score = max(0, 10 - cbs_data["crime_index"])
    green_score = min(10, cbs_data["green_space_percentage"] / 3)
    facilities_score = min(10, sum(demographics["facilities_nearby"].values()) / 10)
    
    location_score = (income_score + safety_score + green_score + facilities_score) / 4
    
    # Market score calculation (0-100 scale)
    price_competitiveness = max(0, 30 - abs(price_delta))  # Max 30 points
    location_quality = location_score * 4  # Max 40 points
    growth_potential = min(30, cbs_data["growth_rate"] * 10)  # Max 30 points
    
    market_score = price_competitiveness + location_quality + growth_potential
    
    # Generate strengths and weaknesses
    strengths = identify_strengths(cbs_data, demographics)
    weaknesses = identify_weaknesses(cbs_data, demographics)
    
    # Investment recommendation
    recommendation = generate_recommendation(market_score, price_delta, location_score)
    
    return {
        "market_score": round(market_score, 1),
        "price_analysis": {
            "asking_price": property.asking_price,
            "avg_comparable_price": round(avg_comp_price, 0),
            "price_difference_pct": round(price_delta, 1),
            "price_per_m2": round(property.asking_price / property.size_m2, 0),
            "avg_price_per_m2_area": round(sum(c["price_per_m2"] for c in comparables) / len(comparables), 0),
            "price_competitiveness_score": round(price_competitiveness, 1)
        },
        "location_analysis": {
            "location_score": round(location_score, 1),
            "income_score": round(income_score, 1),
            "safety_score": round(safety_score, 1),
            "green_score": round(green_score, 1),
            "facilities_score": round(facilities_score, 1),
            "strengths": strengths,
            "weaknesses": weaknesses
        },
        "demographic_insights": demographics,
        "comparable_properties": comparables,
        "investment_recommendation": recommendation
    }

def identify_strengths(cbs_data, demographics):
    """Identify location and market strengths"""
    strengths = []
    
    if cbs_data["average_income"] > 45000:
        strengths.append("Hoog gemiddeld inkomen in de buurt")
    if cbs_data["crime_index"] < 3.5:
        strengths.append("Lage criminaliteitscijfers")
    if cbs_data["growth_rate"] > 3:
        strengths.append("Sterke economische groei")
    if demographics["facilities_nearby"]["schools"] > 5:
        strengths.append("Veel onderwijsvoorzieningen")
    if demographics["facilities_nearby"]["public_transport"] > 7:
        strengths.append("Excellent openbaar vervoer")
    if cbs_data["green_space_percentage"] > 20:
        strengths.append("Veel groenvoorzieningen")
    
    return strengths

def identify_weaknesses(cbs_data, demographics):
    """Identify potential concerns"""
    weaknesses = []
    
    if cbs_data["crime_index"] > 4:
        weaknesses.append("Relatief hoge criminaliteitscijfers")
    if demographics["facilities_nearby"]["public_transport"] < 5:
        weaknesses.append("Beperkte ov-verbindingen")
    if cbs_data["green_space_percentage"] < 10:
        weaknesses.append("Weinig groenvoorzieningen")
    if demographics["employment_rate"] < 92:
        weaknesses.append("Lagere werkgelegenheid dan gemiddeld")
    if demographics.get("commute_time_amsterdam", 0) > 60:
        weaknesses.append("Lange reistijd naar Amsterdam")
    
    return weaknesses

def generate_recommendation(market_score, price_delta, location_score):
    """Generate investment recommendation based on scores"""
    if market_score > 85 and abs(price_delta) < 5:
        return "🟢 STERK KOPEN - Uitstekende investering met goede prijs"
    elif market_score > 75 and abs(price_delta) < 10:
        return "🟢 KOPEN - Goede investering, acceptabele prijs"
    elif market_score > 65 and location_score > 7:
        return "🟡 OVERWEGEN - Goede locatie, prijs kritisch bekijken"
    elif market_score > 50:
        return "🟡 VOORZICHTIG - Nader onderzoek aanbevolen"
    else:
        return "🔴 AFWACHTEN - Risico's overwegen voordelen"

@app.get("/sheets/info")
def get_sheets_info():
    """Get information about connected Google Sheets"""
    return {"test": "sheets endpoint works"}

# For running the API locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "property_research_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )