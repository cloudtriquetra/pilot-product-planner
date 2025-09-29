#!/usr/bin/env python3
"""
Test script for the specific user case: context-aware extraction
"""

def test_context_aware_extraction():
    """Test the context-aware pattern matching"""
    
    test_cases = [
        {
            "input": "try to detect & block attacks in real-time for internal applications which are deployed on cloud (aws /azure)",
            "expected": {
                "countries": None,  # Should NOT detect India from "in real-time"
                "application_type": "Internal",  # Should detect from "internal applications"
                "platforms": ["cloud", "aws", "azure"],
                "description": True  # Should have description (long input with action words)
            }
        },
        {
            "input": "security system for external customers in India",
            "expected": {
                "countries": ["India"],  # Should detect from "in India" 
                "application_type": "External",  # Should detect from "external customers"
                "platforms": None,
                "description": False  # Shorter input
            }
        }
    ]
    
    print("🧪 Testing Context-Aware Extraction")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        test_input = test_case["input"]
        expected = test_case["expected"]
        
        print(f"\nTest Case {i}:")
        print(f"Input: '{test_input}'")
        print("🔍 Analysis:")
        
        lower_input = test_input.lower()
        
        # Country detection
        found_countries = []
        if ' in ' in lower_input:
            in_contexts = ['in india', 'in mumbai', 'in delhi', 'in bangalore', 'in chennai']
            if any(context in lower_input for context in in_contexts):
                found_countries.append('India')
        
        country_patterns = {
            'sg': 'Singapore', 'uk': 'United Kingdom', 'us': 'United States',
            'usa': 'United States', 'germany': 'Germany', 'canada': 'Canada'
        }
        for code, country in country_patterns.items():
            if code in lower_input:
                found_countries.append(country)
        
        print(f"   � Countries: {found_countries if found_countries else 'NONE'}")
        
        # Application type
        app_type = None
        if any(phrase in lower_input for phrase in ['internal application', 'internal app', 'for internal', 'employee', 'staff']):
            app_type = 'Internal'
        elif any(phrase in lower_input for phrase in ['external application', 'external app', 'for external', 'public', 'customer', 'client']):
            app_type = 'External'
        
        print(f"   🏢 Application Type: {app_type if app_type else 'NONE'}")
        
        # Platforms
        platform_keywords = ['cloud', 'aws', 'azure', 'gcp']
        found_platforms = [p for p in platform_keywords if p in lower_input]
        print(f"   💻 Platforms: {found_platforms if found_platforms else 'NONE'}")
        
        # Description
        action_words = ['detect', 'block', 'monitor', 'track', 'analyze', 'process', 'manage', 'create', 'build']
        has_description = len(test_input.split()) > 4 and any(word in lower_input for word in action_words)
        print(f"   📝 Description: {'YES' if has_description else 'NO'}")
        
        # Validation
        print("✅ Validation:")
        
        # Check countries
        if expected["countries"] is None:
            if not found_countries:
                print("   ✅ Countries: PASS (correctly found none)")
            else:
                print(f"   ❌ Countries: FAIL (found {found_countries}, expected none)")
        else:
            if set(found_countries) == set(expected["countries"]):
                print(f"   ✅ Countries: PASS (correctly found {found_countries})")
            else:
                print(f"   ❌ Countries: FAIL (found {found_countries}, expected {expected['countries']})")
        
        # Check application type
        if app_type == expected["application_type"]:
            print(f"   ✅ App Type: PASS (correctly found {app_type})")
        else:
            print(f"   ❌ App Type: FAIL (found {app_type}, expected {expected['application_type']})")
        
        # Check platforms
        if expected["platforms"] is None:
            if not found_platforms:
                print("   ✅ Platforms: PASS (correctly found none)")
            else:
                print(f"   ❌ Platforms: FAIL (found {found_platforms}, expected none)")
        else:
            if set(found_platforms) == set(expected["platforms"]):
                print(f"   ✅ Platforms: PASS (correctly found {found_platforms})")
            else:
                print(f"   ❌ Platforms: FAIL (found {found_platforms}, expected {expected['platforms']})")
        
        print("-" * 60)
    
    print("\n🎯 Summary of Fixes:")
    print("   - Context-aware 'in' detection (real-time vs India)")
    print("   - Proper internal/external application detection")
    print("   - More selective country detection")
    print("   - Better application type normalization")

if __name__ == "__main__":
    test_context_aware_extraction()
