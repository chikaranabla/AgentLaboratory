"""
AI Scientist Agents Module

This module defines AI Scientist agents that conduct research through
GitHub PR/review workflow, inheriting from AgentLaboratory's BaseAgent structure.
"""

from typing import Dict, List, Optional, Tuple
from agents import BaseAgent
from gemini_inference import query_model_gemini
from tools import ArxivSearch, execute_code
from utils import extract_prompt
import copy


class AIScientistAgent(BaseAgent):
    """
    AI Scientist agent that conducts research through GitHub PR/review workflow.
    Inherits from AgentLaboratory's BaseAgent class.
    """
    
    def __init__(self, scientist_id: str, model: str = "gemini-2.0-flash-lite", notes: Optional[List] = None, 
                 max_steps: int = 100, gemini_api_key: Optional[str] = None):
        """
        Initialize AI Scientist agent.
        
        Args:
            scientist_id: "A" or "B"
            model: Gemini model name
            notes: List of notes for the agent
            max_steps: Maximum steps for each phase
            gemini_api_key: Google Gemini API key
        """
        super().__init__(model=model, notes=notes, max_steps=max_steps)
        
        self.scientist_id = scientist_id
        self.gemini_api_key = gemini_api_key
        
        # Research stages
        self.phases = [
            "theme_decision",
            "hypothesis",
            "experiment_plan",
            "experiment_implementation",
            "results_interpretation",
            "paper_writing"
        ]
        
        self.current_stage = 0
        self.stage_names = [
            "研究テーマ決定",
            "仮説提案",
            "実験計画",
            "実験構築",
            "結果解釈",
            "論文執筆"
        ]
        
        # Context storage (critical for maintaining history)
        self.research_theme = None  # Specific research theme
        self.pr_history = []  # PRs created by this scientist and reviews received
        self.review_history = []  # Reviews given to the other scientist
        self.peer_research_context = {}  # Other scientist's research progress
        self.citizen_feedback = []  # Citizen evaluations
        
        # Stage outputs
        self.hypothesis = None
        self.experiment_plan = None
        self.experiment_code = None
        self.results = None
        self.interpretation = None
        self.paper = None
        
        # ArXiv search tool
        self.arxiv_search = ArxivSearch()
    
    def inference(self, research_topic: str, phase: str, step: int, 
                 feedback: str = "", temp: Optional[float] = None) -> str:
        """
        Override inference method to use Gemini API.
        
        Args:
            research_topic: General research topic
            phase: Current phase
            step: Current step number
            feedback: Feedback from previous action
            temp: Temperature for generation
            
        Returns:
            Model response
        """
        sys_prompt = f"""あなたは{self.role_description()}
タスク指示: {self.phase_prompt(phase)}
{self.command_descriptions(phase)}"""
        
        context = self.context(phase)
        history_str = "\n".join([_[1] for _ in self.history])
        phase_notes = [_note for _note in self.notes if phase in _note.get("phases", [])]
        notes_str = f"タスク目標に関するノート: {phase_notes}\n" if len(phase_notes) > 0 else ""
        
        complete_str = ""
        if step / (self.max_steps - 1) > 0.7:
            complete_str = "このタスクをできるだけ早く完了して提出してください！"
        
        prompt = (
            f"""{context}\n{'~' * 10}\n履歴: {history_str}\n{'~' * 10}\n"""
            f"現在のステップ #{step}, フェーズ: {phase}\n{complete_str}\n"
            f"[目標] あなたの目標は以下のトピックについて研究を行うことです: {research_topic}\n"
            f"フィードバック: {feedback}\nノート: {notes_str}\n"
            f"前回のコマンド: {self.prev_comm}. 新しい出力は大きく異なるものにしてください。\n"
            f"以下に単一のコマンドを生成してください:\n"
        )
        
        model_resp = query_model_gemini(
            model_str=self.model,
            system_prompt=sys_prompt,
            prompt=prompt,
            gemini_api_key=self.gemini_api_key,
            temp=temp if temp is not None else 0.7,
            print_cost=False
        )
        
        print("^" * 50, phase, "^" * 50)
        model_resp = self.clean_text(model_resp)
        self.prev_comm = model_resp
        
        steps_exp = None
        if feedback is not None and "```EXPIRATION" in feedback:
            steps_exp = int(feedback.split("\n")[0].replace("```EXPIRATION ", ""))
            feedback = extract_prompt(feedback, "EXPIRATION")
        
        self.history.append((steps_exp, f"Step #{step}, Phase: {phase}, Feedback: {feedback}, Your response: {model_resp}"))
        
        # Remove expired histories
        for _i in reversed(range(len(self.history))):
            if self.history[_i][0] is not None:
                self.history[_i] = (self.history[_i][0] - 1, self.history[_i][1])
                if self.history[_i][0] < 0:
                    self.history.pop(_i)
        
        if len(self.history) >= self.max_hist_len:
            self.history.pop(0)
        
        return model_resp
    
    def decide_research_theme(self, general_topic: str) -> str:
        """
        Decide on a specific research theme based on general topic.
        
        Args:
            general_topic: General research topic provided
            
        Returns:
            Specific research theme
        """
        sys_prompt = f"""あなたは{self.role_description()}
AI研究の専門家として、与えられた大枠の研究テーマから、具体的で実行可能な研究テーマを決定してください。

要件:
1. 明確で具体的な研究課題
2. AI分野における新規性または改良点
3. 実験可能な範囲
4. 論文としてまとめられる内容

具体的な研究テーマを300-500文字で記述してください。"""
        
        prompt = f"""大枠の研究テーマ: {general_topic}

このテーマに基づいて、あなた独自の具体的な研究テーマを決定してください。
以下の形式で回答してください：

```THEME
[具体的な研究テーマの記述]
```"""
        
        response = query_model_gemini(
            model_str=self.model,
            system_prompt=sys_prompt,
            prompt=prompt,
            gemini_api_key=self.gemini_api_key,
            temp=0.8,
            print_cost=False
        )
        
        # Extract theme
        if "```THEME" in response:
            theme = extract_prompt(response, "THEME")
        else:
            theme = response
        
        self.research_theme = theme
        return theme
    
    def create_stage_output(self, stage: str) -> str:
        """
        Create output for a research stage.
        
        Args:
            stage: Stage name
            
        Returns:
            Stage output content
        """
        context = self.context(stage)
        
        sys_prompt = f"""あなたは{self.role_description()}
現在のステージ: {stage}

{self.phase_prompt(stage)}"""
        
        prompt = f"""{context}

上記のコンテキストに基づいて、{stage}の成果物を作成してください。
成果物は詳細で具体的なものにしてください。"""
        
        response = query_model_gemini(
            model_str=self.model,
            system_prompt=sys_prompt,
            prompt=prompt,
            gemini_api_key=self.gemini_api_key,
            temp=0.7,
            print_cost=False
        )
        
        return response
    
    def review_pr(self, pr_content: Dict, pr_author: str) -> Tuple[str, str, str]:
        """
        Review a pull request from the other scientist.
        
        Args:
            pr_content: PR content dictionary
            pr_author: "A" or "B"
            
        Returns:
            Tuple of (review_type, comment, reasoning)
            review_type: "APPROVE", "REQUEST_CHANGES", or "COMMENT"
        """
        # Build context including past reviews given
        review_context = self._build_review_context()
        
        sys_prompt = f"""あなたは{self.role_description()}
研究者{pr_author}のPull Requestをレビューしています。

あなたの役割:
1. 提案された内容の科学的妥当性を評価
2. 実験計画の実行可能性を確認
3. 論理的な一貫性をチェック
4. 改善点があれば具体的に指摘

過去のレビュー履歴:
{review_context}

これまでのレビュー経験を踏まえて、一貫性のある評価を行ってください。"""
        
        pr_summary = f"""PR #{pr_content['number']}: {pr_content['title']}

説明:
{pr_content['body']}

変更されたファイル:
"""
        for filename, content in pr_content['files'].items():
            pr_summary += f"\n=== {filename} ===\n{content[:1000]}...\n"
        
        prompt = f"""{pr_summary}

このPRを評価してください。以下のJSON形式で回答してください：

{{
  "review_type": "APPROVE" または "REQUEST_CHANGES" または "COMMENT",
  "comment": "レビューコメント（具体的なフィードバック）",
  "reasoning": "この判断をした理由"
}}"""
        
        response = query_model_gemini(
            model_str=self.model,
            system_prompt=sys_prompt,
            prompt=prompt,
            gemini_api_key=self.gemini_api_key,
            temp=0.6,
            print_cost=False
        )
        
        # Parse response
        import json
        import re
        
        try:
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                review_type = result.get("review_type", "COMMENT")
                comment = result.get("comment", response)
                reasoning = result.get("reasoning", "")
            else:
                review_type = "COMMENT"
                comment = response
                reasoning = "JSONパースに失敗"
        except:
            review_type = "COMMENT"
            comment = response
            reasoning = "パースエラー"
        
        # Store in review history (CRITICAL: store all reviews)
        self.review_history.append({
            "pr_number": pr_content['number'],
            "pr_author": pr_author,
            "pr_title": pr_content['title'],
            "review_type": review_type,
            "comment": comment,
            "reasoning": reasoning,
            "timestamp": None  # Will be set by simulation
        })
        
        return review_type, comment, reasoning
    
    def _build_review_context(self) -> str:
        """
        Build context string from past reviews given.
        
        Returns:
            Context string with review history
        """
        if not self.review_history:
            return "（まだレビュー履歴がありません）"
        
        context = ""
        for i, review in enumerate(self.review_history[-5:], 1):  # Last 5 reviews
            context += f"\nレビュー{i}:\n"
            context += f"  PR: {review['pr_title']}\n"
            context += f"  判定: {review['review_type']}\n"
            context += f"  コメント: {review['comment'][:200]}...\n"
        
        return context
    
    def context(self, phase: str) -> str:
        """
        Generate context for the current phase.
        
        Args:
            phase: Current phase name
            
        Returns:
            Context string
        """
        context_parts = []
        
        # Research theme
        if self.research_theme:
            context_parts.append(f"あなたの研究テーマ: {self.research_theme}")
        
        # Citizen feedback
        if self.citizen_feedback:
            context_parts.append("\n市民からのフィードバック:")
            for feedback in self.citizen_feedback:
                context_parts.append(
                    f"  - {feedback['citizen_name']}: {feedback['comment'][:100]}... "
                    f"(支援額: {feedback['reward_amount']}円)"
                )
        
        # PR history (reviews received)
        if self.pr_history:
            context_parts.append("\nあなたのPRに対するレビュー履歴:")
            for pr in self.pr_history[-3:]:  # Last 3 PRs
                context_parts.append(
                    f"  PR#{pr.get('number', 'N/A')}: {pr.get('result', 'N/A')} - "
                    f"{pr.get('feedback', '')[:100]}..."
                )
        
        # Review history (reviews given)
        if self.review_history:
            context_parts.append("\nあなたが与えたレビュー履歴:")
            for review in self.review_history[-3:]:  # Last 3 reviews
                context_parts.append(
                    f"  PR#{review['pr_number']}: {review['review_type']} - "
                    f"{review['comment'][:100]}..."
                )
        
        # Previous stage outputs
        if phase in ["experiment_plan", "experiment_implementation", "results_interpretation", "paper_writing"]:
            if self.hypothesis:
                context_parts.append(f"\nあなたの仮説: {self.hypothesis[:200]}...")
        
        if phase in ["experiment_implementation", "results_interpretation", "paper_writing"]:
            if self.experiment_plan:
                context_parts.append(f"\nあなたの実験計画: {self.experiment_plan[:200]}...")
        
        if phase in ["results_interpretation", "paper_writing"]:
            if self.experiment_code:
                context_parts.append(f"\nあなたの実験コード: {self.experiment_code[:200]}...")
            if self.results:
                context_parts.append(f"\nあなたの実験結果: {self.results[:200]}...")
        
        if phase == "paper_writing":
            if self.interpretation:
                context_parts.append(f"\nあなたの結果解釈: {self.interpretation[:200]}...")
        
        return "\n".join(context_parts) if context_parts else "（コンテキストなし）"
    
    def phase_prompt(self, phase: str) -> str:
        """
        Get phase-specific prompt.
        
        Args:
            phase: Phase name
            
        Returns:
            Phase prompt string
        """
        prompts = {
            "theme_decision": "大枠の研究テーマから、具体的で実行可能な研究テーマを決定してください。",
            "hypothesis": "研究テーマに基づいて、検証可能な仮説を提案してください。",
            "experiment_plan": "仮説を検証するための実験計画を立案してください。",
            "experiment_implementation": "実験計画に基づいて、実験を実装してください。",
            "results_interpretation": "実験結果を解釈し、仮説との関係を考察してください。",
            "paper_writing": "研究全体をまとめた論文を執筆してください。"
        }
        return prompts.get(phase, "")
    
    def role_description(self) -> str:
        """Get role description."""
        return f"AI研究分野の研究者{self.scientist_id}です。"
    
    def command_descriptions(self, phase: str) -> str:
        """Get command descriptions for phase."""
        return ""  # Simplified for now
    
    def add_citizen_feedback(self, citizen_name: str, comment: str, 
                            reward_amount: int, reasoning: str):
        """
        Add citizen feedback to context.
        
        Args:
            citizen_name: Name of the citizen
            comment: Citizen's comment
            reward_amount: Support amount
            reasoning: Reasoning for the amount
        """
        self.citizen_feedback.append({
            "citizen_name": citizen_name,
            "comment": comment,
            "reward_amount": reward_amount,
            "reasoning": reasoning
        })
    
    def add_pr_feedback(self, pr_number: int, result: str, feedback: str):
        """
        Add PR feedback received.
        
        Args:
            pr_number: PR number
            result: "APPROVED" or "REJECTED"
            feedback: Review feedback
        """
        self.pr_history.append({
            "number": pr_number,
            "result": result,
            "feedback": feedback
        })

