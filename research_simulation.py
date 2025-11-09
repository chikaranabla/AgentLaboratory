"""
Research Simulation Workflow Module

This module manages the entire simulation workflow where two AI scientists
conduct research through GitHub PR/review process with initial citizen feedback.
"""

import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from github_manager import GitHubManager
from ai_scientist_agents import AIScientistAgent
from citizen_agents import create_citizen_agents
from simulation_logger import SimulationLogger


class ResearchSimulation:
    """
    Manages the research simulation workflow between two AI scientists.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize research simulation.
        
        Args:
            config: Configuration dictionary with all parameters
        """
        self.config = config
        
        # Initialize GitHub managers for each scientist
        # Scientist A's GitHub manager (for repository management and A's PRs)
        self.github_a = GitHubManager(
            access_token=config['github_token_a'],
            repo_owner=config['github_owner'],
            repo_name=config['repo_name']
        )
        
        # Scientist B's GitHub manager (for B's PRs and reviews)
        self.github_b = GitHubManager(
            access_token=config['github_token_b'],
            repo_owner=config['github_owner'],
            repo_name=config['repo_name']
        )
        
        # For backward compatibility, use github_a as default
        self.github = self.github_a
        
        # Initialize logger
        self.logger = SimulationLogger(
            log_dir=config.get('log_dir', './logs'),
            console_output=config.get('console_output', True)
        )
        
        # Initialize AI scientists
        self.scientist_a = AIScientistAgent(
            scientist_id="A",
            model=config.get('gemini_model', 'gemini-2.0-flash-lite'),
            notes=config.get('notes', []),
            max_steps=config.get('max_steps', 100),
            gemini_api_key=config['gemini_api_key']
        )
        
        self.scientist_b = AIScientistAgent(
            scientist_id="B",
            model=config.get('gemini_model', 'gemini-2.0-flash-lite'),
            notes=config.get('notes', []),
            max_steps=config.get('max_steps', 100),
            gemini_api_key=config['gemini_api_key']
        )
        
        # Initialize citizens
        self.citizens = create_citizen_agents(
            gemini_api_key=config['gemini_api_key'],
            model=config.get('gemini_model', 'gemini-2.0-flash-lite')
        )
        
        # Research topic
        self.general_topic = config['research_topic']
        
        # Simulation state
        self.current_step = 0
        self.max_steps = config.get('max_steps', 100)
        self.completed = False
        
        # Stage tracking
        self.stages = [
            "theme_decision",
            "hypothesis",
            "experiment_plan",
            "experiment_implementation",
            "results_interpretation",
            "paper_writing"
        ]
        
        self.scientist_a_stage = 0
        self.scientist_b_stage = 0
    
    def initialize(self):
        """Initialize the simulation: create repo and directory structure."""
        print("\n" + "="*80)
        print("INITIALIZING SIMULATION")
        print("="*80)
        
        # Create repository
        try:
            self.github.create_repository(
                description=f"AI Scientists Research Simulation: {self.general_topic}",
                private=False
            )
            self.logger.log_github_operation(
                "create_repository",
                {"repo_name": self.config['repo_name']}
            )
        except Exception as e:
            self.logger.log_error("GITHUB_ERROR", f"Failed to create repository: {str(e)}")
            raise
        
        # Initialize directory structure
        try:
            self.github.initialize_directory_structure()
            self.logger.log_github_operation(
                "initialize_directory_structure",
                {"directories": ["hypotheses", "experiments", "models", "discussions", "papers"]}
            )
        except Exception as e:
            self.logger.log_error("GITHUB_ERROR", f"Failed to initialize directories: {str(e)}")
            # Continue even if directories already exist
        
        print("\nRepository initialized successfully!")
        print("="*80 + "\n")
    
    def phase_1_theme_decision(self):
        """Phase 1: Both scientists decide their specific research themes."""
        print("\n" + "="*80)
        print("PHASE 1: RESEARCH THEME DECISION")
        print("="*80)
        
        # Scientist A decides theme
        print(f"\nScientist A is deciding research theme...")
        theme_a = self.scientist_a.decide_research_theme(self.general_topic)
        self.logger.log_research_theme_decision("A", theme_a, "Gemini-generated theme")
        print(f"Scientist A's theme: {theme_a}\n")
        
        # Scientist B decides theme
        print(f"Scientist B is deciding research theme...")
        theme_b = self.scientist_b.decide_research_theme(self.general_topic)
        self.logger.log_research_theme_decision("B", theme_b, "Gemini-generated theme")
        print(f"Scientist B's theme: {theme_b}\n")
        
        return theme_a, theme_b
    
    def phase_2_citizen_evaluation(self, theme_a: str, theme_b: str):
        """Phase 2: Citizens evaluate both themes and provide support."""
        print("\n" + "="*80)
        print("PHASE 2: CITIZEN EVALUATION")
        print("="*80)
        
        print("\nCitizens are evaluating the research themes...\n")
        
        for citizen_name, citizen in self.citizens.items():
            print(f"  {citizen_name} is evaluating...")
            
            # Evaluate Scientist A's theme
            comment_a, reward_a, reasoning_a = citizen.evaluate_research_theme(
                "研究者A", theme_a
            )
            self.scientist_a.add_citizen_feedback(
                citizen_name, comment_a, reward_a, reasoning_a
            )
            self.logger.log_citizen_evaluation(
                citizen_name, citizen.persona, "A", theme_a,
                comment_a, reward_a, reasoning_a
            )
            
            # Evaluate Scientist B's theme
            comment_b, reward_b, reasoning_b = citizen.evaluate_research_theme(
                "研究者B", theme_b
            )
            self.scientist_b.add_citizen_feedback(
                citizen_name, comment_b, reward_b, reasoning_b
            )
            self.logger.log_citizen_evaluation(
                citizen_name, citizen.persona, "B", theme_b,
                comment_b, reward_b, reasoning_b
            )
            
            print(f"    Scientist A: {reward_a}円, Scientist B: {reward_b}円")
        
        print("\nCitizen evaluations completed!")
        print("="*80 + "\n")
    
    def conduct_research_stage(self, scientist: AIScientistAgent, stage_idx: int) -> Tuple[str, str, str]:
        """
        Conduct a single research stage for a scientist.
        
        Args:
            scientist: The scientist conducting the stage
            stage_idx: Stage index (0-5)
            
        Returns:
            Tuple of (stage_name, output_content, file_path)
        """
        stage_name = self.stages[stage_idx]
        scientist_id = scientist.scientist_id
        
        print(f"\nScientist {scientist_id} working on: {stage_name}")
        self.logger.log_stage_start(scientist_id, stage_name, stage_idx)
        
        # Create stage output
        output = scientist.create_stage_output(stage_name)
        
        # Determine file path based on stage
        file_paths = {
            "theme_decision": f"discussions/theme_{scientist_id}.md",
            "hypothesis": f"hypotheses/hypothesis_{scientist_id}.md",
            "experiment_plan": f"experiments/plan_{scientist_id}.md",
            "experiment_implementation": f"experiments/code_{scientist_id}.py",
            "results_interpretation": f"experiments/results_{scientist_id}.md",
            "paper_writing": f"papers/draft_{scientist_id}.md"
        }
        
        file_path = file_paths.get(stage_name, f"output_{scientist_id}_{stage_name}.md")
        
        self.logger.log_stage_completion(scientist_id, stage_name, output)
        
        return stage_name, output, file_path
    
    def create_pr_for_stage(self, scientist: AIScientistAgent, stage_name: str, 
                           output: str, file_path: str) -> int:
        """
        Create a GitHub PR for a research stage.
        
        Args:
            scientist: The scientist creating the PR
            stage_name: Name of the stage
            output: Stage output content
            file_path: Path to the file in repository
            
        Returns:
            PR number
        """
        scientist_id = scientist.scientist_id
        branch_name = f"{scientist_id.lower()}-{stage_name}-{int(time.time())}"
        
        # Select appropriate GitHub manager for this scientist
        github_manager = self.github_a if scientist_id == "A" else self.github_b
        
        # Create branch
        github_manager.create_branch(branch_name, "main")
        self.logger.log_github_operation("create_branch", {"branch": branch_name})
        
        # Commit file
        github_manager.commit_file(
            file_path=file_path,
            content=output,
            commit_message=f"[Scientist {scientist_id}] {stage_name}",
            branch=branch_name,
            update=False
        )
        self.logger.log_github_operation(
            "commit_file",
            {"file": file_path, "branch": branch_name}
        )
        
        # Create PR
        pr = github_manager.create_pull_request(
            title=f"[Scientist {scientist_id}] {stage_name}",
            body=f"Scientist {scientist_id}'s work on {stage_name}\n\n{output[:500]}...",
            head_branch=branch_name,
            base_branch="main"
        )
        
        self.logger.log_pr_creation(
            scientist_id, pr.number, pr.title, pr.body,
            branch_name, [file_path]
        )
        
        print(f"  Created PR #{pr.number}")
        
        return pr.number
    
    def review_pr(self, reviewer: AIScientistAgent, pr_number: int,
                 pr_author_id: str) -> Tuple[str, str]:
        """
        Have a scientist review a PR.
        
        Args:
            reviewer: The scientist doing the review
            pr_number: PR number to review
            pr_author_id: ID of the PR author ("A" or "B")
            
        Returns:
            Tuple of (review_type, comment)
        """
        reviewer_id = reviewer.scientist_id
        
        print(f"\nScientist {reviewer_id} reviewing PR #{pr_number}...")
        
        # Select appropriate GitHub manager for reviewer
        reviewer_github = self.github_a if reviewer_id == "A" else self.github_b
        
        # Get PR content (can use any github manager for reading)
        pr_content = self.github.get_pr_content(pr_number)
        
        # Get review decision
        review_type, comment, reasoning = reviewer.review_pr(pr_content, pr_author_id)
        
        # Post review to GitHub using reviewer's account
        if review_type == "APPROVE":
            reviewer_github.approve_pr(pr_number, comment)
        elif review_type == "REQUEST_CHANGES":
            reviewer_github.reject_pr(pr_number, comment)
        else:
            reviewer_github.add_pr_comment(pr_number, comment)
        
        self.logger.log_pr_review(
            reviewer_id, pr_number, pr_author_id,
            review_type, comment, reasoning,
            context_used={"review_history_length": len(reviewer.review_history)}
        )
        
        print(f"  Review: {review_type}")
        
        return review_type, comment
    
    def run_simulation(self):
        """Run the complete simulation."""
        try:
            # Initialize
            self.initialize()
            
            # Phase 1: Theme decision
            theme_a, theme_b = self.phase_1_theme_decision()
            
            # Phase 2: Citizen evaluation
            self.phase_2_citizen_evaluation(theme_a, theme_b)
            
            # Main research loop
            print("\n" + "="*80)
            print("MAIN RESEARCH LOOP")
            print("="*80)
            
            while self.current_step < self.max_steps and not self.completed:
                self.current_step += 1
                print(f"\n{'='*80}")
                print(f"STEP {self.current_step}")
                print(f"{'='*80}")
                
                self.logger.log_step(
                    self.current_step,
                    f"Scientist A stage {self.scientist_a_stage}, Scientist B stage {self.scientist_b_stage}"
                )
                
                # Scientist A's turn
                if self.scientist_a_stage < len(self.stages):
                    stage_name, output, file_path = self.conduct_research_stage(
                        self.scientist_a, self.scientist_a_stage
                    )
                    pr_number = self.create_pr_for_stage(
                        self.scientist_a, stage_name, output, file_path
                    )
                    
                    # Scientist B reviews
                    review_type, comment = self.review_pr(
                        self.scientist_b, pr_number, "A"
                    )
                    
                    if review_type == "APPROVE":
                        # Merge PR
                        self.github.merge_pr(pr_number)
                        self.logger.log_pr_merge(pr_number, "A")
                        self.scientist_a.add_pr_feedback(pr_number, "APPROVED", comment)
                        self.scientist_a_stage += 1
                        print(f"  Scientist A advances to stage {self.scientist_a_stage}")
                    else:
                        # Retry
                        self.scientist_a.add_pr_feedback(pr_number, "REJECTED", comment)
                        self.logger.log_stage_retry("A", stage_name, comment[:100])
                        print(f"  Scientist A must retry stage {self.scientist_a_stage}")
                
                # Scientist B's turn
                if self.scientist_b_stage < len(self.stages):
                    stage_name, output, file_path = self.conduct_research_stage(
                        self.scientist_b, self.scientist_b_stage
                    )
                    pr_number = self.create_pr_for_stage(
                        self.scientist_b, stage_name, output, file_path
                    )
                    
                    # Scientist A reviews
                    review_type, comment = self.review_pr(
                        self.scientist_a, pr_number, "B"
                    )
                    
                    if review_type == "APPROVE":
                        # Merge PR
                        self.github.merge_pr(pr_number)
                        self.logger.log_pr_merge(pr_number, "B")
                        self.scientist_b.add_pr_feedback(pr_number, "APPROVED", comment)
                        self.scientist_b_stage += 1
                        print(f"  Scientist B advances to stage {self.scientist_b_stage}")
                    else:
                        # Retry
                        self.scientist_b.add_pr_feedback(pr_number, "REJECTED", comment)
                        self.logger.log_stage_retry("B", stage_name, comment[:100])
                        print(f"  Scientist B must retry stage {self.scientist_b_stage}")
                
                # Check completion
                if (self.scientist_a_stage >= len(self.stages) and
                    self.scientist_b_stage >= len(self.stages)):
                    self.completed = True
                    print("\n" + "="*80)
                    print("BOTH SCIENTISTS COMPLETED ALL STAGES!")
                    print("="*80)
                    break
                
                # Small delay to avoid rate limits
                time.sleep(2)
            
            # Finalize
            self.logger.finalize()
            
            print("\n" + "="*80)
            print("SIMULATION COMPLETED SUCCESSFULLY")
            print("="*80)
            
        except Exception as e:
            self.logger.log_error("SIMULATION_ERROR", str(e))
            self.logger.finalize()
            raise


# Example usage
if __name__ == "__main__":
    import os
    
    config = {
        'github_token': os.getenv('GITHUB_TOKEN'),
        'github_owner': os.getenv('GITHUB_OWNER', 'your-username'),
        'repo_name': 'ai-scientists-research-test',
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'research_topic': '自然言語処理における感情分析の改良',
        'max_steps': 50,
        'log_dir': './logs',
        'console_output': True
    }
    
    sim = ResearchSimulation(config)
    sim.run_simulation()

