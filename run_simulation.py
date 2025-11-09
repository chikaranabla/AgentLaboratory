"""
Main Execution Script for AI Scientists Simulation

This script runs the complete simulation with configuration from:
1. Command-line arguments (highest priority)
2. .env file (for API keys)
3. config.yaml file (for other settings)
4. Default values (lowest priority)
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from dotenv import load_dotenv

from research_simulation import ResearchSimulation


def load_config(config_path: str = "./config.yaml") -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config if config else {}


def merge_configs(yaml_config: dict, env_config: dict, args_config: dict) -> dict:
    """
    Merge configurations with priority: args > env > yaml > defaults.
    
    Args:
        yaml_config: Configuration from YAML file
        env_config: Configuration from environment variables
        args_config: Configuration from command-line arguments
        
    Returns:
        Merged configuration dictionary
    """
    # Default configuration
    config = {
        'research_topic': '自然言語処理における感情分析',
        'max_steps': 100,
        'repo_name': 'ai-scientists-research',
        'log_dir': './logs',
        'console_output': True,
        'gemini_model': 'gemini-2.0-flash-lite',
        'temperature': 0.7,
        'max_tokens': 2048,
        'notes': []
    }
    
    # Merge YAML config
    if yaml_config:
        if 'research' in yaml_config:
            config['research_topic'] = yaml_config['research'].get('topic', config['research_topic'])
            config['max_steps'] = yaml_config['research'].get('max_steps', config['max_steps'])
        
        if 'github' in yaml_config:
            config['repo_name'] = yaml_config['github'].get('repo_name', config['repo_name'])
            config['github_owner'] = yaml_config['github'].get('owner', env_config.get('github_owner', ''))
        
        if 'logging' in yaml_config:
            config['log_dir'] = yaml_config['logging'].get('log_dir', config['log_dir'])
            config['console_output'] = yaml_config['logging'].get('console_output', config['console_output'])
        
        if 'gemini' in yaml_config:
            config['gemini_model'] = yaml_config['gemini'].get('model', config['gemini_model'])
            config['temperature'] = yaml_config['gemini'].get('temperature', config['temperature'])
            config['max_tokens'] = yaml_config['gemini'].get('max_tokens', config['max_tokens'])
    
    # Merge environment config
    config.update({k: v for k, v in env_config.items() if v is not None})
    
    # Merge command-line args (highest priority)
    config.update({k: v for k, v in args_config.items() if v is not None})
    
    return config


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Run AI Scientists Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Priority (highest to lowest):
  1. Command-line arguments
  2. Environment variables (.env file)
  3. Configuration file (config.yaml)
  4. Default values

Example usage:
  python run_simulation.py
  python run_simulation.py --research-topic "機械学習の解釈可能性"
  python run_simulation.py --config my_config.yaml --max-steps 50
        """
    )
    
    # Configuration file
    parser.add_argument(
        '--config',
        type=str,
        default='./config.yaml',
        help='Path to config.yaml file (default: ./config.yaml)'
    )
    
    # API Keys
    parser.add_argument(
        '--github-token-a',
        type=str,
        help='GitHub Personal Access Token for Scientist A (overrides .env)'
    )
    
    parser.add_argument(
        '--github-token-b',
        type=str,
        help='GitHub Personal Access Token for Scientist B (overrides .env)'
    )
    
    parser.add_argument(
        '--gemini-api-key',
        type=str,
        help='Google Gemini API key (overrides .env)'
    )
    
    # Research settings
    parser.add_argument(
        '--research-topic',
        type=str,
        help='General research topic (overrides config.yaml)'
    )
    
    parser.add_argument(
        '--max-steps',
        type=int,
        help='Maximum simulation steps (overrides config.yaml)'
    )
    
    # GitHub settings
    parser.add_argument(
        '--repo-name',
        type=str,
        help='GitHub repository name (overrides config.yaml)'
    )
    
    parser.add_argument(
        '--github-owner',
        type=str,
        help='GitHub username/owner (overrides .env and config.yaml)'
    )
    
    # Logging settings
    parser.add_argument(
        '--log-dir',
        type=str,
        help='Log directory path (overrides config.yaml)'
    )
    
    parser.add_argument(
        '--no-console',
        action='store_true',
        help='Disable console output'
    )
    
    # Gemini settings
    parser.add_argument(
        '--model',
        type=str,
        choices=['gemini-2.0-flash-lite', 'gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash'],
        help='Gemini model to use (overrides config.yaml)'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    print("="*80)
    print("AI SCIENTISTS SIMULATION")
    print("="*80)
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Load environment variables from .env file
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv()
        print("\n✓ Loaded environment variables from .env")
    else:
        print("\n⚠ No .env file found. Please create one from env_example.txt")
    
    # Load YAML configuration
    yaml_config = load_config(args.config)
    if yaml_config:
        print(f"✓ Loaded configuration from {args.config}")
    
    # Get environment variables
    env_config = {
        'github_token_a': os.getenv('GITHUB_TOKEN_A'),
        'github_token_b': os.getenv('GITHUB_TOKEN_B'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'github_owner': os.getenv('GITHUB_OWNER')
    }
    
    # Get command-line arguments
    args_config = {
        'github_token_a': getattr(args, 'github_token_a', None),
        'github_token_b': getattr(args, 'github_token_b', None),
        'gemini_api_key': args.gemini_api_key,
        'research_topic': args.research_topic,
        'max_steps': args.max_steps,
        'repo_name': args.repo_name,
        'github_owner': args.github_owner,
        'log_dir': args.log_dir,
        'console_output': not args.no_console,
        'gemini_model': args.model
    }
    
    # Merge all configurations
    config = merge_configs(yaml_config, env_config, args_config)
    
    # Validate required parameters
    if not config.get('github_token_a'):
        print("\n❌ ERROR: GitHub token A (Scientist A) not provided!")
        print("Please set GITHUB_TOKEN_A in .env file or use --github-token-a argument")
        sys.exit(1)
    
    if not config.get('github_token_b'):
        print("\n❌ ERROR: GitHub token B (Scientist B) not provided!")
        print("Please set GITHUB_TOKEN_B in .env file or use --github-token-b argument")
        sys.exit(1)
    
    if not config.get('gemini_api_key'):
        print("\n❌ ERROR: Gemini API key not provided!")
        print("Please set GEMINI_API_KEY in .env file or use --gemini-api-key argument")
        sys.exit(1)
    
    if not config.get('github_owner'):
        print("\n❌ ERROR: GitHub owner/username not provided!")
        print("Please set GITHUB_OWNER in .env file, config.yaml, or use --github-owner argument")
        sys.exit(1)
    
    # Display configuration
    print("\n" + "="*80)
    print("CONFIGURATION")
    print("="*80)
    print(f"Research Topic: {config['research_topic']}")
    print(f"Max Steps: {config['max_steps']}")
    print(f"GitHub Owner: {config['github_owner']}")
    print(f"Repository: {config['repo_name']}")
    print(f"Gemini Model: {config['gemini_model']}")
    print(f"Log Directory: {config['log_dir']}")
    print("="*80)
    
    # Confirm to proceed
    try:
        response = input("\nProceed with simulation? [y/N]: ").strip().lower()
        if response != 'y':
            print("Simulation cancelled.")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nSimulation cancelled.")
        sys.exit(0)
    
    # Run simulation
    try:
        print("\nStarting simulation...")
        simulation = ResearchSimulation(config)
        simulation.run_simulation()
        
        print("\n" + "="*80)
        print("✓ SIMULATION COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"\nLogs saved to: {config['log_dir']}")
        print(f"GitHub Repository: https://github.com/{config['github_owner']}/{config['repo_name']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: Simulation failed!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

