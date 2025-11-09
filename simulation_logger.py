"""
Simulation Logger Module

This module provides comprehensive logging for the AI scientists simulation,
recording all events, actions, reviews, and statistical information.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class SimulationLogger:
    """
    Comprehensive logger for AI scientists simulation.
    Logs all events, actions, reviews, and statistics in both JSON and text formats.
    """
    
    def __init__(self, log_dir: str = "./logs", console_output: bool = True):
        """
        Initialize the simulation logger.
        
        Args:
            log_dir: Directory to store log files
            console_output: Whether to also print logs to console
        """
        self.log_dir = Path(log_dir)
        self.console_output = console_output
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize log storage
        self.events = []
        self.statistics = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_steps": 0,
            "total_prs": 0,
            "approved_prs": 0,
            "rejected_prs": 0,
            "scientist_a": {
                "theme": None,
                "current_stage": 0,
                "prs_created": 0,
                "prs_approved": 0,
                "prs_rejected": 0,
                "reviews_given": 0,
                "retries": 0
            },
            "scientist_b": {
                "theme": None,
                "current_stage": 0,
                "prs_created": 0,
                "prs_approved": 0,
                "prs_rejected": 0,
                "reviews_given": 0,
                "retries": 0
            },
            "citizen_rewards": {
                "total_amount": 0,
                "average_amount": 0,
                "distribution": []
            },
            "stage_durations": {}
        }
        
        # Log file paths
        self.json_log_path = self.log_dir / "simulation_log.json"
        self.text_log_path = self.log_dir / "simulation_log.txt"
        
        # Open text log file
        self.text_log_file = open(self.text_log_path, 'w', encoding='utf-8')
        
        self._log_event("SIMULATION_START", "Simulation logger initialized")
    
    def _log_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """
        Internal method to log an event.
        
        Args:
            event_type: Type of event
            description: Human-readable description
            data: Additional event data
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "data": data or {}
        }
        self.events.append(event)
        
        # Write to text log
        log_line = f"[{event['timestamp']}] {event_type}: {description}\n"
        if data:
            log_line += f"  Data: {json.dumps(data, indent=2, ensure_ascii=False)}\n"
        
        self.text_log_file.write(log_line)
        self.text_log_file.flush()
        
        if self.console_output:
            print(log_line.strip())
    
    def log_research_theme_decision(self, scientist_id: str, theme: str, 
                                   thought_process: str):
        """
        Log research theme decision by a scientist.
        
        Args:
            scientist_id: "A" or "B"
            theme: Specific research theme decided
            thought_process: The scientist's decision-making process
        """
        self.statistics[f"scientist_{scientist_id.lower()}"]["theme"] = theme
        
        self._log_event(
            "RESEARCH_THEME_DECISION",
            f"Scientist {scientist_id} decided on research theme",
            {
                "scientist": scientist_id,
                "theme": theme,
                "thought_process": thought_process
            }
        )
    
    def log_citizen_evaluation(self, citizen_name: str, citizen_persona: str,
                              scientist_id: str, theme: str, comment: str, 
                              reward_amount: int, reasoning: str):
        """
        Log citizen evaluation of research theme.
        
        Args:
            citizen_name: Name of the citizen
            citizen_persona: Citizen's persona description
            scientist_id: "A" or "B"
            theme: Research theme being evaluated
            comment: Citizen's opinion/comment
            reward_amount: Support amount (1-1000 yen)
            reasoning: Reason for the reward amount
        """
        self.statistics["citizen_rewards"]["distribution"].append({
            "citizen": citizen_name,
            "scientist": scientist_id,
            "amount": reward_amount
        })
        
        self._log_event(
            "CITIZEN_EVALUATION",
            f"Citizen {citizen_name} evaluated Scientist {scientist_id}'s theme",
            {
                "citizen_name": citizen_name,
                "citizen_persona": citizen_persona,
                "scientist": scientist_id,
                "theme": theme,
                "comment": comment,
                "reward_amount": reward_amount,
                "reasoning": reasoning
            }
        )
    
    def log_stage_start(self, scientist_id: str, stage_name: str, stage_number: int):
        """
        Log start of a research stage.
        
        Args:
            scientist_id: "A" or "B"
            stage_name: Name of the stage
            stage_number: Stage number (0-5)
        """
        stage_key = f"{scientist_id}_{stage_name}_{datetime.now().isoformat()}"
        self.statistics["stage_durations"][stage_key] = {
            "scientist": scientist_id,
            "stage": stage_name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": None
        }
        
        self._log_event(
            "STAGE_START",
            f"Scientist {scientist_id} started {stage_name}",
            {
                "scientist": scientist_id,
                "stage": stage_name,
                "stage_number": stage_number
            }
        )
    
    def log_stage_completion(self, scientist_id: str, stage_name: str, 
                            output: str):
        """
        Log completion of a research stage.
        
        Args:
            scientist_id: "A" or "B"
            stage_name: Name of the stage
            output: Stage output/result
        """
        # Update stage duration
        for stage_key in reversed(list(self.statistics["stage_durations"].keys())):
            stage_info = self.statistics["stage_durations"][stage_key]
            if (stage_info["scientist"] == scientist_id and 
                stage_info["stage"] == stage_name and 
                stage_info["end_time"] is None):
                start_time = datetime.fromisoformat(stage_info["start_time"])
                end_time = datetime.now()
                stage_info["end_time"] = end_time.isoformat()
                stage_info["duration_seconds"] = (end_time - start_time).total_seconds()
                break
        
        self._log_event(
            "STAGE_COMPLETION",
            f"Scientist {scientist_id} completed {stage_name}",
            {
                "scientist": scientist_id,
                "stage": stage_name,
                "output": output[:500] + "..." if len(output) > 500 else output
            }
        )
    
    def log_pr_creation(self, scientist_id: str, pr_number: int, title: str,
                       description: str, branch: str, files_changed: List[str]):
        """
        Log pull request creation.
        
        Args:
            scientist_id: "A" or "B"
            pr_number: GitHub PR number
            title: PR title
            description: PR description
            branch: Source branch
            files_changed: List of files changed
        """
        self.statistics["total_prs"] += 1
        self.statistics[f"scientist_{scientist_id.lower()}"]["prs_created"] += 1
        
        self._log_event(
            "PR_CREATED",
            f"Scientist {scientist_id} created PR #{pr_number}",
            {
                "scientist": scientist_id,
                "pr_number": pr_number,
                "title": title,
                "description": description,
                "branch": branch,
                "files_changed": files_changed
            }
        )
    
    def log_pr_review(self, reviewer_id: str, pr_number: int, pr_author: str,
                     review_type: str, comment: str, reasoning: str,
                     context_used: Optional[Dict] = None):
        """
        Log pull request review.
        
        Args:
            reviewer_id: "A" or "B" (who is reviewing)
            pr_number: GitHub PR number
            pr_author: "A" or "B" (who created the PR)
            review_type: "APPROVE", "REQUEST_CHANGES", or "COMMENT"
            comment: Review comment (full text)
            reasoning: Reasoning for the decision
            context_used: What context was used for the review
        """
        self.statistics[f"scientist_{reviewer_id.lower()}"]["reviews_given"] += 1
        
        if review_type == "APPROVE":
            self.statistics["approved_prs"] += 1
            self.statistics[f"scientist_{pr_author.lower()}"]["prs_approved"] += 1
        elif review_type == "REQUEST_CHANGES":
            self.statistics["rejected_prs"] += 1
            self.statistics[f"scientist_{pr_author.lower()}"]["prs_rejected"] += 1
        
        self._log_event(
            "PR_REVIEW",
            f"Scientist {reviewer_id} reviewed PR #{pr_number} from Scientist {pr_author}: {review_type}",
            {
                "reviewer": reviewer_id,
                "pr_number": pr_number,
                "pr_author": pr_author,
                "review_type": review_type,
                "comment": comment,
                "reasoning": reasoning,
                "context_used": context_used or {}
            }
        )
    
    def log_pr_merge(self, pr_number: int, scientist_id: str):
        """
        Log pull request merge.
        
        Args:
            pr_number: GitHub PR number
            scientist_id: "A" or "B" (whose PR was merged)
        """
        self._log_event(
            "PR_MERGED",
            f"PR #{pr_number} from Scientist {scientist_id} was merged",
            {
                "pr_number": pr_number,
                "scientist": scientist_id
            }
        )
    
    def log_stage_retry(self, scientist_id: str, stage_name: str, reason: str):
        """
        Log stage retry (when PR is rejected).
        
        Args:
            scientist_id: "A" or "B"
            stage_name: Name of the stage being retried
            reason: Reason for retry
        """
        self.statistics[f"scientist_{scientist_id.lower()}"]["retries"] += 1
        
        self._log_event(
            "STAGE_RETRY",
            f"Scientist {scientist_id} retrying {stage_name}",
            {
                "scientist": scientist_id,
                "stage": stage_name,
                "reason": reason
            }
        )
    
    def log_step(self, step_number: int, description: str, details: Optional[Dict] = None):
        """
        Log a simulation step.
        
        Args:
            step_number: Current step number
            description: Step description
            details: Additional step details
        """
        self.statistics["total_steps"] = step_number
        
        self._log_event(
            "SIMULATION_STEP",
            f"Step {step_number}: {description}",
            details or {}
        )
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """
        Log an error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Error context
        """
        self._log_event(
            "ERROR",
            f"{error_type}: {error_message}",
            context or {}
        )
    
    def log_github_operation(self, operation: str, details: Dict):
        """
        Log GitHub API operation.
        
        Args:
            operation: Operation name (e.g., "create_branch", "commit_file")
            details: Operation details
        """
        self._log_event(
            "GITHUB_OPERATION",
            f"GitHub operation: {operation}",
            details
        )
    
    def log_llm_call(self, agent: str, prompt_length: int, response_length: int,
                    model: str, purpose: str):
        """
        Log LLM API call.
        
        Args:
            agent: Agent making the call (e.g., "Scientist_A", "Citizen_1")
            prompt_length: Length of prompt in characters
            response_length: Length of response in characters
            model: Model used
            purpose: Purpose of the call
        """
        self._log_event(
            "LLM_CALL",
            f"{agent} called {model} for {purpose}",
            {
                "agent": agent,
                "model": model,
                "purpose": purpose,
                "prompt_length": prompt_length,
                "response_length": response_length
            }
        )
    
    def finalize(self):
        """
        Finalize the simulation and write complete logs.
        """
        self.statistics["end_time"] = datetime.now().isoformat()
        
        # Calculate citizen rewards statistics
        if self.statistics["citizen_rewards"]["distribution"]:
            amounts = [r["amount"] for r in self.statistics["citizen_rewards"]["distribution"]]
            self.statistics["citizen_rewards"]["total_amount"] = sum(amounts)
            self.statistics["citizen_rewards"]["average_amount"] = sum(amounts) / len(amounts)
        
        # Calculate approval rate
        if self.statistics["total_prs"] > 0:
            self.statistics["approval_rate"] = (
                self.statistics["approved_prs"] / self.statistics["total_prs"]
            )
            self.statistics["rejection_rate"] = (
                self.statistics["rejected_prs"] / self.statistics["total_prs"]
            )
        
        # Write statistics summary to text log before closing
        if not self.text_log_file.closed:
            summary = "\n" + "="*80 + "\n"
            summary += "SIMULATION STATISTICS SUMMARY\n"
            summary += "="*80 + "\n"
            summary += json.dumps(self.statistics, indent=2, ensure_ascii=False)
            summary += "\n" + "="*80 + "\n"
            
            self.text_log_file.write(summary)
            self.text_log_file.close()
        
        # Write complete JSON log
        complete_log = {
            "statistics": self.statistics,
            "events": self.events
        }
        
        with open(self.json_log_path, 'w', encoding='utf-8') as f:
            json.dump(complete_log, f, indent=2, ensure_ascii=False)
        
        if self.console_output:
            print("\n" + "="*80)
            print("SIMULATION COMPLETED")
            print("="*80)
            print(f"Total Steps: {self.statistics['total_steps']}")
            print(f"Total PRs: {self.statistics['total_prs']}")
            print(f"Approved: {self.statistics['approved_prs']}")
            print(f"Rejected: {self.statistics['rejected_prs']}")
            if self.statistics.get('approval_rate'):
                print(f"Approval Rate: {self.statistics['approval_rate']:.2%}")
            print(f"\nLogs saved to:")
            print(f"  JSON: {self.json_log_path}")
            print(f"  Text: {self.text_log_path}")
            print("="*80)
    
    def __del__(self):
        """Cleanup: close text log file if still open."""
        if hasattr(self, 'text_log_file') and not self.text_log_file.closed:
            self.text_log_file.close()

