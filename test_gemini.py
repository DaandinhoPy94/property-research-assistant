# test_gemini.py - Test Gemini integration separately
import asyncio
import sys
import os

# Add api directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from ai_analyzer import ai_analyzer

async def test_gemini():
    """Test Gemini AI analysis"""
    
    # Test property data
    property_data = {
        "address": "Kalverstraat 1",
        "city": "Amsterdam",
        "postal_code": "1012NX",
        "property_type": "apartment",
        "size_m2": 85,
        "asking_price": 450000
    }
    
    # Test market analysis data
    market_analysis = {
        "market_score": 87.5,
        "price_analysis": {
            "asking_price": 450000,
            "avg_comparable_price": 447600,
            "price_difference_pct": 0.5
        },
        "location_analysis": {
            "location_score": 7.0,
            "strengths": ["Hoog inkomen", "Goede locatie"],
            "weaknesses": ["Drukte"]
        },
        "demographic_insights": {
            "population_growth": 2.8,
            "employment_rate": 94.5,
            "average_income": 52000
        },
        "comparable_properties": [
            {"address": "Test 1", "sold_price": 450000, "size_m2": 80}
        ]
    }
    
    print("🧪 Testing Gemini AI Analysis...")
    
    try:
        # Test comprehensive analysis
        ai_result = await ai_analyzer.generate_comprehensive_analysis(
            property_data, 
            market_analysis
        )
        
        print("✅ Gemini Analysis Result:")
        print(f"Executive Summary: {ai_result.get('executive_summary', 'Missing')}")
        print(f"Investment Grade: {ai_result.get('investment_grade', 'Missing')}")
        print(f"Bottom Line: {ai_result.get('bottom_line', 'Missing')}")
        
        # Test market insights
        market_result = await ai_analyzer.generate_market_insights(
            "Amsterdam",
            {"average_income": 52000, "population_growth": 2.8}
        )
        
        print("\n✅ Market Insights Result:")
        print(f"Market Outlook: {market_result.get('market_outlook', 'Missing')}")
        print(f"Investment Timing: {market_result.get('investment_timing', 'Missing')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_gemini())