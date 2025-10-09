#!/usr/bin/env python3
"""
Quick test script to verify LLM tool detection implementation.
Run this to check if the changes work correctly.
"""

def test_imports():
    """Test that all imports work."""
    print("=" * 60)
    print("TEST 1: Checking Imports")
    print("=" * 60)
    
    try:
        from cccp.prompts import get_prompt, PromptConfig
        print("✅ Prompt system imports work")
    except Exception as e:
        print(f"❌ Prompt import failed: {e}")
        return False
    
    try:
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        print("✅ Agent import works")
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        return False
    
    return True

def test_prompt_generation():
    """Test that prompts can be generated."""
    print("\n" + "=" * 60)
    print("TEST 2: Prompt Generation")
    print("=" * 60)
    
    try:
        from cccp.prompts import get_prompt
        
        prompt = get_prompt(
            "tool_detection",
            user_input="What happened to my order 2?",
            tools_info="Tool: getorder\nDescription: Get order information"
        )
        
        print(f"✅ Prompt generated successfully")
        print(f"   Length: {len(prompt)} characters")
        print(f"   Preview: {prompt[:150]}...")
        
        # Check if it's using Llama format
        if "<|begin_of_text|>" in prompt:
            print("✅ Using Llama 3.2 optimized format (v2)")
        elif "You are a tool detection assistant" in prompt:
            print("✅ Using basic format (v1)")
        
        return True
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        return False

def test_agent_methods():
    """Test that agent has new methods."""
    print("\n" + "=" * 60)
    print("TEST 3: Agent New Methods")
    print("=" * 60)
    
    try:
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        
        # Check if new methods exist
        methods = [
            '_get_tools_info',
            '_get_tool_parameters',
            '_validate_and_clean_json',
            '_fallback_tool_detection'
        ]
        
        for method in methods:
            if hasattr(agent, method):
                print(f"✅ Method exists: {method}")
            else:
                print(f"❌ Method missing: {method}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Agent method check failed: {e}")
        return False

def test_tools_info():
    """Test that tools info can be generated."""
    print("\n" + "=" * 60)
    print("TEST 4: Tools Information Extraction")
    print("=" * 60)
    
    try:
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        tools_info = agent._get_tools_info()
        
        print(f"✅ Tools info extracted successfully")
        print(f"   Available tools detected: {len(agent.available_tools)}")
        print(f"\n   Tools info preview:")
        print(f"   {tools_info[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Tools info extraction failed: {e}")
        return False

def test_json_validation():
    """Test JSON validation and cleaning."""
    print("\n" + "=" * 60)
    print("TEST 5: JSON Validation")
    print("=" * 60)
    
    try:
        from cccp.agents.custom_tool_calling_agent import CustomToolCallingAgent
        
        agent = CustomToolCallingAgent()
        
        # Test with clean JSON
        test_json = '{"tool_name": "getorder", "parameters": {"cart_id": "2"}, "confidence": 0.85}'
        result = agent._validate_and_clean_json(test_json)
        print(f"✅ Clean JSON parsed: {result}")
        
        # Test with markdown wrapper
        test_json_markdown = '```json\n{"tool_name": "multiply", "parameters": {"a": 5, "b": 3}}\n```'
        result = agent._validate_and_clean_json(test_json_markdown)
        print(f"✅ Markdown-wrapped JSON parsed: {result}")
        
        return True
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False

def test_configuration():
    """Test prompt configuration."""
    print("\n" + "=" * 60)
    print("TEST 6: Prompt Configuration")
    print("=" * 60)
    
    try:
        from cccp.prompts import PromptConfig
        from cccp.prompts.config import PromptVersion
        
        active_version = PromptConfig.get_active_version("tool_detection")
        print(f"✅ Active version: {active_version.value}")
        
        metadata = PromptConfig.get_metadata(active_version)
        print(f"✅ Metadata retrieved:")
        print(f"   Description: {metadata.get('description')}")
        print(f"   Best for: {metadata.get('best_for')}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n")
    print("🧪 LLM TOOL DETECTION - VERIFICATION TESTS")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Prompt Generation", test_prompt_generation()))
    results.append(("Agent Methods", test_agent_methods()))
    results.append(("Tools Info", test_tools_info()))
    results.append(("JSON Validation", test_json_validation()))
    results.append(("Configuration", test_configuration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 SUCCESS! All implementation checks passed.")
        print("\nNext steps:")
        print("1. Run your full system to test with actual LLM")
        print("2. Try query: 'What happened to my order 2?'")
        print("3. Check logs for '✅ LLM detected tool:'")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

