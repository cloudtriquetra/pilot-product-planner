#!/usr/bin/env python3
"""
Test script for multi-field extraction functionality
"""

def test_extraction_patterns():
    """Test the enhanced pattern matching"""
    
    # Test case 1: Short input (should only extract name)
    test_input_short = "runtime detection"
    print("🧪 Testing Multi-Field Extraction")
    print("=" * 60)
    print(f"Test 1 - Short Input: '{test_input_short}'")
    print("Expected: Only name extraction, NO description or constraints")
    
    input_words = test_input_short.strip().split()
    if len(input_words) >= 2:
        first_two_words = ' '.join(input_words[:2])
        name_indicators = ['runtime', 'security', 'detection', 'monitoring', 'tracking']
        if any(word.lower() in first_two_words.lower() for word in name_indicators):
            project_name = first_two_words.title()
            print(f"🏷️ Name: {project_name}")
    
    # Check if description should be extracted (should be NO for short input)
    action_words = ['detect', 'block', 'monitor', 'track', 'analyze', 'process', 'manage', 'create', 'build']
    lower_input = test_input_short.lower()
    if len(test_input_short.split()) > 4 and any(word in lower_input for word in action_words):
        print(f"📝 Description: {test_input_short}")
    else:
        print("📝 Description: NONE (input too short)")
    
    # Check constraints (should be NO for short input)
    constraint_keywords = ['response time', 'data privacy', 'mobile-friendly', 'gdpr', 'compliance']
    if len(test_input_short.split()) > 5:
        print(f"⚠️ Constraints: Would check for keywords")
    else:
        print("⚠️ Constraints: NONE (input too short)")
    
    print("\n" + "=" * 60)
    
    # Test case 2: Long detailed input
    test_input_long = "Runtime detection - try to detect & block attacks in real-time for applications with response time requirements deployed on cloud (aws /azure) in sg, in & uk."
    print(f"Test 2 - Long Input: '{test_input_long}'")
    print("Expected: Multiple field extraction")
    
    # Name extraction
    input_words = test_input_long.strip().split()
    if len(input_words) >= 2:
        first_two_words = ' '.join(input_words[:2])
        name_indicators = ['runtime', 'security', 'detection', 'monitoring', 'tracking']
        if any(word.lower() in first_two_words.lower() for word in name_indicators):
            project_name = first_two_words.title()
            print(f"🏷️ Name: {project_name}")
    
    # Country detection
    country_patterns = {
        'sg': 'Singapore', 'in': 'India', 'uk': 'United Kingdom'
    }
    found_countries = []
    lower_input_long = test_input_long.lower()
    for code, country in country_patterns.items():
        if code in lower_input_long:
            found_countries.append(country)
    
    print(f"🌍 Countries: {', '.join(found_countries)}")
    
    # Platform detection
    platform_keywords = ['cloud', 'aws', 'azure']
    found_platforms = []
    for platform in platform_keywords:
        if platform in lower_input_long:
            found_platforms.append(platform.upper())
    
    print(f"💻 Platforms: {', '.join(found_platforms)}")
    
    # Description extraction (now requires longer input)
    if len(test_input_long.split()) > 4 and any(word in lower_input_long for word in action_words):
        print(f"📝 Description: {test_input_long}")
    else:
        print("📝 Description: NONE")
    
    # Constraints (now looks for specific keywords)
    constraint_keywords = ['response time', 'data privacy', 'mobile-friendly', 'gdpr', 'compliance']
    found_constraints = []
    if len(test_input_long.split()) > 5:
        for constraint in constraint_keywords:
            if constraint in lower_input_long:
                found_constraints.append(constraint)
    
    if found_constraints:
        print(f"⚠️ Constraints: {', '.join(found_constraints)}")
    else:
        print("⚠️ Constraints: NONE (no specific constraint keywords found)")
    
    print("\n✅ Improved extraction logic:")
    print("   - Short inputs: Only extract name")
    print("   - Long inputs: Extract multiple fields")
    print("   - Constraints: Wait for specific requirement keywords")
    
    return {
        'short_test': test_input_short,
        'long_test': test_input_long,
        'improvement': 'More selective extraction'
    }

if __name__ == "__main__":
    results = test_extraction_patterns()
    print(f"\n📊 Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
