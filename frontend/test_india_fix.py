#!/usr/bin/env python3
"""
Quick test for the specific issue
"""

def test_india_detection():
    """Test that 'in real-time' doesn't trigger India detection"""
    
    test_input = "try to detect & block attacks in real-time for internal applications which are deployed on cloud (aws /azure)"
    lower_input = test_input.lower()
    
    print("🧪 Testing India Detection Fix")
    print("=" * 50)
    print(f"Input: '{test_input}'")
    
    # Test the fixed logic
    found_countries = []
    
    # Special handling for 'in' - only if it's clearly a country reference
    if ' in ' in lower_input:
        # Check if 'in' is followed by context that suggests it's India
        in_contexts = ['in india', 'in mumbai', 'in delhi', 'in bangalore', 'in chennai']
        if any(context in lower_input for context in in_contexts):
            found_countries.append('India')
            print("✅ Found India context")
        else:
            print("❌ No India context found (correctly)")
    
    # Check other country codes with word boundaries
    import re
    country_patterns = {
        'sg': 'Singapore', 'uk': 'United Kingdom', 'us': 'United States',
        'usa': 'United States', 'germany': 'Germany', 'canada': 'Canada'
    }
    
    for code, country in country_patterns.items():
        if re.search(r'\b' + re.escape(code) + r'\b', lower_input):
            found_countries.append(country)
            print(f"✅ Found {country} from code '{code}'")
    
    print(f"\n🌍 Final countries detected: {found_countries}")
    
    if not found_countries:
        print("✅ SUCCESS: No false positive country detection!")
    else:
        print("❌ FAIL: Still detecting countries incorrectly")
    
    # Test with a valid India case
    print("\n" + "=" * 50)
    test_input2 = "security system for customers in India"
    lower_input2 = test_input2.lower()
    print(f"Test 2 Input: '{test_input2}'")
    
    found_countries2 = []
    if ' in ' in lower_input2:
        in_contexts = ['in india', 'in mumbai', 'in delhi', 'in bangalore', 'in chennai']
        if any(context in lower_input2 for context in in_contexts):
            found_countries2.append('India')
            print("✅ Correctly found India")
    
    for code, country in country_patterns.items():
        if re.search(r'\b' + re.escape(code) + r'\b', lower_input2):
            found_countries2.append(country)
    
    print(f"🌍 Countries detected: {found_countries2}")
    
    if 'India' in found_countries2:
        print("✅ SUCCESS: Correctly detected India when appropriate!")
    else:
        print("❌ FAIL: Should have detected India")

if __name__ == "__main__":
    test_india_detection()
