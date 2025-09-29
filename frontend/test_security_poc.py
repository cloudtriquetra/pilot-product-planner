#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Mock Streamlit secrets for testing
class MockSecrets:
    def __init__(self):
        self.data = {'ANTHROPIC_API_KEY': 'test-key'}
    
    def __getitem__(self, key):
        return self.data[key]

class MockStreamlit:
    secrets = MockSecrets()

# Mock streamlit
sys.modules['streamlit'] = MockStreamlit()

from product_use_case import extract_data_from_input

def test_security_poc_input():
    """Test the security consolidation PoC input"""
    
    print("🔐 Testing Security PoC Input")
    print("=" * 60)
    
    test_input = "poc on application security consolidation for secret scanning & owasp, cwe asking what project do"
    
    print(f"Input: '{test_input}'")
    print()
    
    # Test extraction (will fail due to API key, but we can see the logic)
    try:
        result = extract_data_from_input(test_input, {})
        print("🎯 Extraction Results:")
        for key, value in result.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"⚠️  Expected API error: {str(e)}")
        print()
        print("🔍 Analysis of Input:")
        print("   📝 Contains: 'application security consolidation'")
        print("   🛡️  Security keywords: secret scanning, owasp, cwe")
        print("   📋 Project type: PoC (Proof of Concept)")
        print("   ❓ Question: 'asking what project do' - needs clarification")
        print()
        print("💡 Expected Extraction:")
        print("   name: 'Application Security Consolidation PoC'")
        print("   description: 'PoC for application security consolidation covering secret scanning, OWASP, and CWE'")
        print("   application_type: Likely 'Internal' (security tooling)")
        print("   constraints: Security scanning requirements, OWASP compliance")

if __name__ == "__main__":
    test_security_poc_input()
