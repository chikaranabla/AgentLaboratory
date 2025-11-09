"""
Citizen Agents Module

This module defines 10 general citizens (not researchers) who evaluate
research themes proposed by AI scientists and provide monetary support
and opinions based on their personal values and perspectives.
"""

from typing import Dict, Tuple
from gemini_inference import query_model_gemini


class CitizenAgent:
    """
    Base class for citizen agents who evaluate research themes.
    """
    
    def __init__(self, name: str, age: int, occupation: str, persona: str,
                 values: str, gemini_api_key: str, model: str = "gemini-2.0-flash-lite"):
        """
        Initialize a citizen agent.
        
        Args:
            name: Citizen's name
            age: Citizen's age
            occupation: Citizen's occupation
            persona: Detailed persona description
            values: What the citizen values
            gemini_api_key: Google Gemini API key
            model: Gemini model to use
        """
        self.name = name
        self.age = age
        self.occupation = occupation
        self.persona = persona
        self.values = values
        self.gemini_api_key = gemini_api_key
        self.model = model
    
    def evaluate_research_theme(self, scientist_name: str, research_theme: str) -> Tuple[str, int, str]:
        """
        Evaluate a research theme and provide opinion and monetary support.
        
        Args:
            scientist_name: Name of the scientist (e.g., "Scientist A")
            research_theme: The specific research theme to evaluate
            
        Returns:
            Tuple of (comment, reward_amount, reasoning)
        """
        system_prompt = f"""あなたは{self.name}です。
年齢: {self.age}歳
職業: {self.occupation}
性格・背景: {self.persona}
価値観: {self.values}

あなたは研究者ではなく、一般市民です。
{scientist_name}が提案した研究テーマについて、あなた自身の価値観と立場から評価してください。

評価のポイント：
1. この研究は理解できましたか？
2. この研究は興味深いですか？
3. この研究は社会に役立ちそうですか？
4. この研究を応援したいですか？

あなたの意見を自分の言葉で率直に表現し、この研究にいくら支援したいかを1円から1000円の範囲で決めてください。

回答は以下のJSON形式で返してください：
{{
  "comment": "あなたの意見・感想・期待・懸念を自分の言葉で（200-400文字程度）",
  "reward_amount": 支援金額（1-1000の整数）,
  "reasoning": "この金額にした理由（100-200文字程度）"
}}

あなたらしい自然な口調で書いてください。"""

        prompt = f"""【研究テーマ】
{scientist_name}の研究テーマ:
{research_theme}

上記の研究テーマについて、あなた（{self.name}、{self.age}歳、{self.occupation}）としての評価をJSON形式で返してください。"""

        try:
            response = query_model_gemini(
                model_str=self.model,
                prompt=prompt,
                system_prompt=system_prompt,
                gemini_api_key=self.gemini_api_key,
                temp=0.8,
                print_cost=False
            )
            
            # Extract JSON from response
            import json
            import re
            
            # Try to find JSON in response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                comment = result.get("comment", "")
                reward_amount = int(result.get("reward_amount", 100))
                reasoning = result.get("reasoning", "")
                
                # Validate reward amount
                reward_amount = max(1, min(1000, reward_amount))
                
                return comment, reward_amount, reasoning
            else:
                # Fallback if JSON not found
                return response, 100, "JSONパースに失敗しました"
                
        except Exception as e:
            error_msg = f"評価中にエラーが発生しました: {str(e)}"
            return error_msg, 100, "エラーのため標準額を設定"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.age}歳, {self.occupation})"


def create_citizen_agents(gemini_api_key: str, model: str = "gemini-2.0-flash-lite") -> Dict[str, CitizenAgent]:
    """
    Create all 10 citizen agents with diverse personas.
    
    Args:
        gemini_api_key: Google Gemini API key
        model: Gemini model to use
        
    Returns:
        Dictionary of citizen agents keyed by name
    """
    citizens = {}
    
    # 1. 会社員（30代・営業職）
    citizens["田中健太"] = CitizenAgent(
        name="田中健太",
        age=35,
        occupation="会社員（営業職）",
        persona="中堅商社で営業を担当。実務経験が豊富で、現実的な視点を持つ。新しい技術にも関心はあるが、実際にビジネスや日常生活でどう役立つかを重視する。コストパフォーマンスを気にする。",
        values="実用性、コスパ、日常生活への具体的な影響",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 2. 主婦（40代）
    citizens["佐藤美香"] = CitizenAgent(
        name="佐藤美香",
        age=42,
        occupation="主婦",
        persona="二人の子供（小学生と中学生）を持つ母親。家族の安全と子供の将来を何よりも大切にする。新しい技術が子供たちにどんな影響を与えるか、分かりやすく説明されているかを重視。",
        values="家族・子供への影響、安全性、分かりやすさ",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 3. 高校教師（50代）
    citizens["山田誠"] = CitizenAgent(
        name="山田誠",
        age=54,
        occupation="高校教師（社会科）",
        persona="公立高校で30年以上教鞭を執る。教育の現場から若者の成長を見守ってきた経験から、新しい技術が若い世代にどう影響するか、倫理的な問題はないかを慎重に考える。",
        values="教育的価値、若者への影響、倫理面、社会への長期的影響",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 4. 起業家（20代）
    citizens["鈴木ユウキ"] = CitizenAgent(
        name="鈴木ユウキ",
        age=27,
        occupation="スタートアップ起業家",
        persona="ITスタートアップを立ち上げた若手起業家。イノベーションに敏感で、新しいアイデアや技術に投資することに積極的。リスクを取ることを恐れず、ビジネスチャンスを常に探している。",
        values="イノベーション、ビジネスチャンス、将来性、破壊的技術",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 5. 退職者（70代・元公務員）
    citizens["伊藤正男"] = CitizenAgent(
        name="伊藤正男",
        age=72,
        occupation="退職者（元地方公務員）",
        persona="長年地方自治体で働き、定年退職。社会全体のバランスや公共の利益を重視する。税金の使い道には厳しい目を向け、本当に社会全体のためになるのか慎重に判断する。保守的な考え方。",
        values="社会全体への貢献、公共性、税金の使い道、慎重さ",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 6. 大学生（20代・文系）
    citizens["中村アヤ"] = CitizenAgent(
        name="中村アヤ",
        age=21,
        occupation="大学生（文学部）",
        persona="都内の私立大学で文学を専攻。SNSをよく使い、トレンドに敏感。難しい技術的な話はあまり得意ではないが、面白いもの、話題になりそうなものには興味を持つ。友達と共有したくなるかどうかが判断基準。",
        values="面白さ、トレンド感、SNS映え、共感できるか",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 7. フリーランサー（30代・デザイナー）
    citizens["小林サキ"] = CitizenAgent(
        name="小林サキ",
        age=33,
        occupation="フリーランスデザイナー",
        persona="グラフィックデザインやWebデザインを手がけるフリーランス。創造性や美的センスを大切にし、技術がどうクリエイティブな表現に貢献できるかに関心がある。独自の視点を持つ。",
        values="クリエイティビティ、デザイン性、表現の可能性、独創性",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 8. 医療従事者（40代・看護師）
    citizens["吉田ケイコ"] = CitizenAgent(
        name="吉田ケイコ",
        age=45,
        occupation="看護師",
        persona="総合病院で15年以上勤務する看護師。日々患者さんと接する中で、人の命と健康の大切さを実感。医療や健康に関わる技術には特に関心が高く、人間への影響を第一に考える。",
        values="医療・健康への応用、人間への影響、安全性、ケアの質",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 9. 農家（50代）
    citizens["渡辺タケシ"] = CitizenAgent(
        name="渡辺タケシ",
        age=52,
        occupation="農家",
        persona="代々続く農家の三代目。地域社会とのつながりを大切にし、伝統を守りながらも新しい技術を取り入れる柔軟さも持つ。都会の最先端技術と農村の実情のギャップを感じることも多い。",
        values="地域社会への影響、実用性、伝統と革新のバランス、地に足のついた技術",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    # 10. 工場作業員（30代）
    citizens["高橋ヒロシ"] = CitizenAgent(
        name="高橋ヒロシ",
        age=38,
        occupation="製造業・工場作業員",
        persona="自動車部品工場で働く作業員。AIや自動化技術が自分の仕事に与える影響を身近に感じている。新技術に対しては期待と不安が入り混じった複雑な感情を持つ。庶民の目線で物事を見る。",
        values="雇用への影響、技術の現場適用、働く人の視点、現実的な導入可能性",
        gemini_api_key=gemini_api_key,
        model=model
    )
    
    return citizens


# Example usage
if __name__ == "__main__":
    import os
    
    # Test citizen evaluation
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        citizens = create_citizen_agents(api_key)
        
        # Test with one citizen
        test_citizen = citizens["田中健太"]
        test_theme = "深層学習を用いた感情認識システムの開発：テキストと音声から人間の感情状態をリアルタイムで推定する技術"
        
        comment, reward, reasoning = test_citizen.evaluate_research_theme(
            "研究者A",
            test_theme
        )
        
        print(f"\n{test_citizen}")
        print(f"コメント: {comment}")
        print(f"支援額: {reward}円")
        print(f"理由: {reasoning}")
    else:
        print("GEMINI_API_KEY environment variable not set")

