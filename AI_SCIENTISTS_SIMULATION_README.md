# AI Scientists Simulation

2人のAI研究者が、GitHub PR/レビューシステムを通じて共同研究を行うシミュレーションシステムです。市民エージェントからの初期評価とフィードバックを受けて、研究を進めていきます。

## 概要

このシミュレーションは以下の特徴を持ちます：

- **2人のAI Scientists**: 独立して研究テーマを決定し、仮説→実験→論文執筆まで実施
- **GitHub統合**: 実際のGitHub APIを使用し、リアルなPR/レビューワークフロー
- **10人の市民エージェント**: 多様なペルソナを持つ一般市民が研究テーマを評価し、支援金を決定
- **コンテキスト保持**: すべてのレビューコメント、市民評価を次のアクションに反映
- **包括的ログ**: 全イベント、発言、決定を詳細に記録
- **Google Gemini**: すべてのLLM推論にGemini APIを使用

## システム構成

### 主要モジュール

1. **github_manager.py** - GitHub API統合（リポジトリ、PR、レビュー管理）
2. **gemini_inference.py** - Google Gemini API統合
3. **simulation_logger.py** - 詳細ログシステム
4. **citizen_agents.py** - 10人の市民エージェント
5. **ai_scientist_agents.py** - AI Scientistエージェント（BaseAgentを継承）
6. **research_simulation.py** - シミュレーションワークフロー管理
7. **run_simulation.py** - メイン実行スクリプト

### 市民エージェント（10人）

1. **田中健太** (35歳, 営業職) - 実用性とコスパ重視
2. **佐藤美香** (42歳, 主婦) - 家族・子供への影響重視
3. **山田誠** (54歳, 高校教師) - 教育的価値と倫理面
4. **鈴木ユウキ** (27歳, 起業家) - イノベーション志向
5. **伊藤正男** (72歳, 退職者) - 社会貢献と慎重さ
6. **中村アヤ** (21歳, 大学生) - 面白さとトレンド感
7. **小林サキ** (33歳, デザイナー) - クリエイティビティ重視
8. **吉田ケイコ** (45歳, 看護師) - 医療・健康への応用
9. **渡辺タケシ** (52歳, 農家) - 地域社会への影響
10. **高橋ヒロシ** (38歳, 工場作業員) - 雇用への影響と実用性

## セットアップ

### 1. 依存関係のインストール

```bash
cd AgentLaboratory
pip install -r requirements.txt
```

### 2. APIキーの設定

#### `.env`ファイルの作成

`env_example.txt`を参考に、`.env`ファイルを作成：

```bash
# .env
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_OWNER=your-github-username
```

**GitHub Token取得方法:**
1. https://github.com/settings/tokens にアクセス
2. "Generate new token (classic)" をクリック
3. スコープで`repo`（フルコントロール）を選択
4. トークンを生成してコピー

**Gemini API Key取得方法:**
1. https://makersuite.google.com/app/apikey にアクセス
2. APIキーを作成
3. キーをコピー

### 3. 設定ファイルの編集

`config.yaml`を編集（または`config.example.yaml`からコピー）：

```yaml
research:
  topic: "自然言語処理における感情分析の改良"  # 研究トピックを指定
  max_steps: 100

github:
  repo_name: "ai-scientists-research"
  owner: "your-github-username"  # あなたのGitHubユーザー名に変更

logging:
  log_dir: "./logs"
  console_output: true

agents:
  review_strictness: "medium"
  stage_timeout: 300

gemini:
  model: "gemini-pro"  # または gemini-1.5-pro, gemini-1.5-flash
  temperature: 0.7
  max_tokens: 2048
```

## 実行方法

### 基本的な実行

```bash
python run_simulation.py
```

### コマンドライン引数で設定を上書き

```bash
# 研究トピックを指定
python run_simulation.py --research-topic "機械学習の解釈可能性向上"

# 最大ステップ数を指定
python run_simulation.py --max-steps 50

# 別の設定ファイルを使用
python run_simulation.py --config my_config.yaml

# リポジトリ名を指定
python run_simulation.py --repo-name my-research-repo

# Geminiモデルを指定
python run_simulation.py --model gemini-1.5-pro

# コンソール出力を無効化
python run_simulation.py --no-console
```

### 設定の優先順位

1. **コマンドライン引数**（最優先）
2. **環境変数**（.envファイル）
3. **設定ファイル**（config.yaml）
4. **デフォルト値**（最低優先）

## シミュレーションフロー

### 初期化フェーズ

1. GitHubリポジトリ作成
2. ディレクトリ構造初期化（hypotheses/, experiments/, papers/など）

### 研究テーマ決定フェーズ

1. Scientist Aが具体的な研究テーマを決定
2. Scientist Bが具体的な研究テーマを決定
3. 10人の市民が両方のテーマを評価
   - 意見・感想を表明
   - 支援金額（1-1000円）を決定

### メインループ（研究フェーズ）

各研究者が以下のステージを順次実行：

0. **研究テーマ決定** → 市民評価
1. **仮説提案** → PRレビュー
2. **実験計画** → PRレビュー
3. **実験構築** → PRレビュー
4. **結果解釈** → PRレビュー
5. **論文執筆** → PRレビュー

#### 各ステージの流れ

1. Scientist Aがステージを実行 → PR作成
2. Scientist BがPRをレビュー
   - **APPROVE**: Aは次ステージへ進む
   - **REQUEST_CHANGES**: Aは同じステージをやり直し
3. Scientist Bがステージを実行 → PR作成
4. Scientist AがPRをレビュー
   - **APPROVE**: Bは次ステージへ進む
   - **REQUEST_CHANGES**: Bは同じステージをやり直し

### 終了条件

- 両方のScientistが全ステージ（論文執筆まで）完了
- または最大ステップ数に到達

## ログとデータ

### ログファイル

シミュレーション実行後、以下のログが生成されます：

- `logs/simulation_log.json` - 構造化されたJSON形式の完全ログ
- `logs/simulation_log.txt` - 可読性の高いテキスト形式ログ

### ログ内容

- すべてのイベントのタイムスタンプ
- 研究テーマ決定プロセス
- 市民評価（全コメント、支援金額、理由）
- PRの作成・レビュー・マージ履歴
- **AI Scientistが与えたレビューコメント（全文、Approve/Reject両方）**
- **AI Scientistが受け取ったレビューコメント（全文）**
- GitHub操作履歴
- 統計情報（PR総数、承認率、やり直し回数など）

### GitHub リポジトリ

実際のGitHubリポジトリが作成され、以下が記録されます：

- 各ステージの成果物（仮説、実験計画、コード、論文など）
- PRとレビューの完全な履歴
- コミット履歴

リポジトリURL: `https://github.com/{GITHUB_OWNER}/{repo_name}`

## コンテキスト保持

AI Scientistエージェントは以下を常にコンテキストとして保持：

1. **自分が出したPR**と**受け取ったレビュー**（全文、Approve/Reject両方）
2. **自分が相手に与えたレビュー**（全文、Approve/Reject両方）
3. **市民からの評価**（意見と支援金額）
4. **相手の研究進捗状況**
5. **過去の全ステージの成果物**

これにより、一貫性のある研究とレビューが可能になります。

## トラブルシューティング

### GitHub API エラー

**エラー:** `Bad credentials`
- **原因:** GitHub tokenが無効または期限切れ
- **解決:** 新しいtokenを生成して`.env`を更新

**エラー:** `Repository already exists`
- **原因:** 同名のリポジトリが既に存在
- **解決:** `config.yaml`で別の`repo_name`を指定

### Gemini API エラー

**エラー:** `API key not valid`
- **原因:** APIキーが無効
- **解決:** 正しいAPIキーを`.env`に設定

**エラー:** `Resource exhausted` / `Quota exceeded`
- **原因:** APIクォータ/レート制限
- **解決:** しばらく待ってから再実行、またはモデルを変更（`gemini-1.5-flash`は安い）

### その他

**PRレビューが失敗する**
- PRの内容が大きすぎる場合、Gemini APIのトークン制限に到達する可能性
- `max_tokens`を増やすか、モデルを変更

**シミュレーションが遅い**
- Gemini APIの呼び出しには時間がかかります
- `max_steps`を減らして短いシミュレーションに

## 開発者向け情報

### AgentLaboratoryとの統合

このシミュレーションは既存の`AgentLaboratory`コードベースを活用：

- `BaseAgent`クラスを継承
- `history`、`inference()`、`context()`メソッドを活用
- `ArxivSearch`、`execute_code`などのツールを利用

### カスタマイズ

#### 市民エージェントの追加

`citizen_agents.py`の`create_citizen_agents()`関数を編集して、新しい市民を追加できます。

#### 研究ステージの変更

`ai_scientist_agents.py`の`phases`リストと`phase_prompt()`メソッドを編集。

#### レビュー厳格度の調整

`config.yaml`の`agents.review_strictness`を変更（現在は未実装、将来の拡張ポイント）。

## ライセンス

このプロジェクトは`AgentLaboratory`プロジェクトの一部です。

## 参考

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Google Gemini API](https://ai.google.dev/docs)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)

