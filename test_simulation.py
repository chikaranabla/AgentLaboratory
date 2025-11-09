"""
Test Script for AI Scientists Simulation

This script performs basic validation of all components without running
the full simulation. Use this to verify your setup before running the full simulation.
"""

import os
import sys
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "="*80)
    print("TEST 1: Module Imports")
    print("="*80)
    
    modules = [
        ('github', 'PyGithub'),
        ('google.generativeai', 'google-generativeai'),
        ('yaml', 'PyYAML'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_passed = True
    for module_name, package_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {package_name} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {package_name}: {e}")
            all_passed = False
    
    # Test our custom modules
    custom_modules = [
        'github_manager',
        'gemini_inference',
        'simulation_logger',
        'citizen_agents',
        'ai_scientist_agents',
        'research_simulation',
        'run_simulation'
    ]
    
    for module_name in custom_modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name}.py imported successfully")
        except Exception as e:
            print(f"✗ Failed to import {module_name}.py: {e}")
            all_passed = False
    
    return all_passed


def test_config_files():
    """Test that configuration files exist."""
    print("\n" + "="*80)
    print("TEST 2: Configuration Files")
    print("="*80)
    
    files = {
        '.env': 'Environment variables (API keys)',
        'config.yaml': 'Simulation configuration',
        'env_example.txt': 'Example environment file',
        'config.example.yaml': 'Example config file'
    }
    
    all_passed = True
    for filename, description in files.items():
        filepath = Path(filename)
        if filepath.exists():
            print(f"✓ {filename} exists - {description}")
        else:
            if filename in ['.env']:
                print(f"⚠ {filename} not found - {description} (create from env_example.txt)")
                all_passed = False
            else:
                print(f"✓ {filename} found - {description}")
    
    return all_passed


def test_env_variables():
    """Test that required environment variables are set."""
    print("\n" + "="*80)
    print("TEST 3: Environment Variables")
    print("="*80)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'GITHUB_TOKEN': 'GitHub Personal Access Token',
        'GEMINI_API_KEY': 'Google Gemini API Key',
        'GITHUB_OWNER': 'GitHub username'
    }
    
    all_passed = True
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value and value != f'your_{var_name.lower()}_here':
            print(f"✓ {var_name} is set - {description}")
        else:
            print(f"✗ {var_name} not set - {description}")
            all_passed = False
    
    return all_passed


def test_gemini_api():
    """Test Gemini API connection."""
    print("\n" + "="*80)
    print("TEST 4: Gemini API Connection")
    print("="*80)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("✗ Gemini API key not configured")
            return False
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try a simple test
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = model.generate_content("Say 'Hello' in one word")
        
        if response and hasattr(response, 'text'):
            print(f"✓ Gemini API connection successful")
            print(f"  Test response: {response.text[:50]}")
            return True
        else:
            print("✗ Gemini API returned unexpected response")
            return False
            
    except Exception as e:
        print(f"✗ Gemini API test failed: {str(e)}")
        return False


def test_github_api():
    """Test GitHub API connection."""
    print("\n" + "="*80)
    print("TEST 5: GitHub API Connection")
    print("="*80)
    
    try:
        from dotenv import load_dotenv
        from github import Github, Auth
        
        load_dotenv()
        
        token = os.getenv('GITHUB_TOKEN')
        if not token or token == 'your_github_token_here':
            print("✗ GitHub token not configured")
            return False
        
        auth = Auth.Token(token)
        github = Github(auth=auth)
        user = github.get_user()
        
        print(f"✓ GitHub API connection successful")
        print(f"  Authenticated as: {user.login}")
        print(f"  Name: {user.name}")
        print(f"  Public repos: {user.public_repos}")
        
        # Check API rate limit (handle different PyGithub versions)
        try:
            rate_limit = github.get_rate_limit()
            if hasattr(rate_limit, 'core'):
                print(f"  API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
            else:
                print(f"  API rate limit: Available")
        except Exception as e:
            print(f"  API rate limit: (check skipped)")
        
        return True
        
    except Exception as e:
        print(f"✗ GitHub API test failed: {str(e)}")
        return False


def test_citizen_agents():
    """Test citizen agent creation."""
    print("\n" + "="*80)
    print("TEST 6: Citizen Agents")
    print("="*80)
    
    try:
        from dotenv import load_dotenv
        from citizen_agents import create_citizen_agents
        
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("⚠ Skipping citizen agents test (no API key)")
            return True
        
        citizens = create_citizen_agents(api_key)
        
        if len(citizens) == 10:
            print(f"✓ Created {len(citizens)} citizen agents")
            for name, citizen in list(citizens.items())[:3]:
                print(f"  - {name}: {citizen.occupation}")
            print(f"  ... and {len(citizens) - 3} more")
            return True
        else:
            print(f"✗ Expected 10 citizens, got {len(citizens)}")
            return False
            
    except Exception as e:
        print(f"✗ Citizen agents test failed: {str(e)}")
        return False


def test_ai_scientist_creation():
    """Test AI Scientist agent creation."""
    print("\n" + "="*80)
    print("TEST 7: AI Scientist Agents")
    print("="*80)
    
    try:
        from dotenv import load_dotenv
        from ai_scientist_agents import AIScientistAgent
        
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("⚠ Skipping AI scientist test (no API key)")
            return True
        
        scientist = AIScientistAgent(
            scientist_id="A",
            gemini_api_key=api_key
        )
        
        print(f"✓ Created AI Scientist agent")
        print(f"  ID: {scientist.scientist_id}")
        print(f"  Stages: {len(scientist.phases)}")
        print(f"  Current stage: {scientist.current_stage}")
        
        return True
        
    except Exception as e:
        print(f"✗ AI Scientist test failed: {str(e)}")
        return False


def test_logger():
    """Test simulation logger."""
    print("\n" + "="*80)
    print("TEST 8: Simulation Logger")
    print("="*80)
    
    try:
        from simulation_logger import SimulationLogger
        import tempfile
        import shutil
        
        # Create temporary log directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            logger = SimulationLogger(log_dir=temp_dir, console_output=False)
            
            # Test logging various events
            logger.log_research_theme_decision("A", "Test theme", "Test process")
            logger.log_citizen_evaluation("TestCitizen", "Test persona", "A", 
                                         "Test theme", "Test comment", 500, "Test reason")
            logger.log_step(1, "Test step")
            
            logger.finalize()
            
            # Check if log files were created
            log_files = list(Path(temp_dir).glob("*.json")) + list(Path(temp_dir).glob("*.txt"))
            
            if len(log_files) >= 2:
                print(f"✓ Logger created {len(log_files)} log files")
                return True
            else:
                print(f"✗ Expected at least 2 log files, got {len(log_files)}")
                return False
                
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"✗ Logger test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("AI SCIENTISTS SIMULATION - SYSTEM VALIDATION")
    print("="*80)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Files", test_config_files),
        ("Environment Variables", test_env_variables),
        ("Gemini API", test_gemini_api),
        ("GitHub API", test_github_api),
        ("Citizen Agents", test_citizen_agents),
        ("AI Scientists", test_ai_scientist_creation),
        ("Logger", test_logger),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' raised exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready for simulation.")
        print("\nTo run the simulation:")
        print("  python run_simulation.py")
    else:
        print("\n⚠ Some tests failed. Please fix the issues before running simulation.")
        print("\nCommon fixes:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Create .env file from env_example.txt")
        print("  3. Add your API keys to .env file")
        print("  4. Update config.yaml with your GitHub username")
    
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

