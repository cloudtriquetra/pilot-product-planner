#!/usr/bin/env python3
"""
Test the fixed extraction logic
"""

# Simulate the improved extraction logic
def test_fixed_extraction():
    test_input = "try to detect & block attacks in real-time for internal applications which are deployed on cloud (aws /azure)"
    lower_input = test_input.lower()
    
    print("🧪 Testing Fixed Extraction Logic")
    print("=" * 60)
    print(f"Input: '{test_input}'")
    print("\n🔍 Analysis:")
    
    # Country detection (improved with context checking)
    country_patterns = {
        'sg': 'Singapore', 'uk': 'United Kingdom', 'us': 'United States',
        'usa': 'United States', 'germany': 'Germany', 'canada': 'Canada'
    }
    
    found_countries = []
    
    # Special handling for 'in' - only if it's clearly a country reference
    if ' in ' in lower_input:
        in_contexts = ['in india', 'in mumbai', 'in delhi', 'in bangalore', 'in chennai']
        if any(context in lower_input for context in in_contexts):
            found_countries.append('India')
            print("   ✅ Found India from context")
        else:
            print("   ❌ No India context found - 'in' is part of 'in real-time' (CORRECT)")
    
    # Check other country codes with word boundaries
    import re
    for code, country in country_patterns.items():
        if re.search(r'\b' + re.escape(code) + r'\b', lower_input):
            found_countries.append(country)
            print(f"   ✅ Found {country} from code '{code}'")
    
    print(f"🌍 Countries: {found_countries if found_countries else 'NONE'}")
    
    # Application type detection
    app_type = None
    if any(phrase in lower_input for phrase in ['internal application', 'internal app', 'for internal', 'employee', 'staff']):
        app_type = 'Internal'
        print("   ✅ Found Internal application")
    elif any(phrase in lower_input for phrase in ['external application', 'external app', 'for external', 'public', 'customer', 'client']):
        app_type = 'External'
        print("   ✅ Found External application")
    
    print(f"🏢 Application Type: {app_type}")
    
    # Platform detection
    platform_keywords = ['cloud', 'aws', 'azure', 'gcp']
    found_platforms = [p for p in platform_keywords if p in lower_input]
    print(f"💻 Platforms: {found_platforms}")
    
    # Description (should be present for longer inputs)
    action_words = ['detect', 'block', 'monitor', 'track', 'analyze', 'process', 'manage', 'create', 'build']
    has_description = len(test_input.split()) > 4 and any(word in lower_input for word in action_words)
    print(f"📝 Description: {'YES' if has_description else 'NO'}")
    
    print("\n✅ Expected Results:")
    print("   🌍 Countries: NONE (correctly avoiding 'in real-time' false positive)")
    print("   🏢 Application Type: Internal (from 'internal applications')")
    print("   💻 Platforms: cloud, aws, azure")
    print("   📝 Description: YES (long input with action words)")
    
    print("\n🎯 Test Results:")
    
    # Validate countries
    if not found_countries:
        print("   ✅ Countries: PASS - No false positive from 'in real-time'")
    else:
        print(f"   ❌ Countries: FAIL - Still detecting {found_countries}")
    
    # Validate application type
    if app_type == 'Internal':
        print("   ✅ Application Type: PASS - Correctly detected Internal")
    else:
        print(f"   ❌ Application Type: FAIL - Got {app_type}, expected Internal")
    
    # Validate platforms
    if set(found_platforms) == {'cloud', 'aws', 'azure'}:
        print("   ✅ Platforms: PASS - Correctly detected all platforms")
    else:
        print(f"   ❌ Platforms: FAIL - Got {found_platforms}")
    
    # Validate description
    if has_description:
        print("   ✅ Description: PASS - Correctly identified as descriptive text")
    else:
        print("   ❌ Description: FAIL - Should have description")

if __name__ == "__main__":
    test_fixed_extraction()
