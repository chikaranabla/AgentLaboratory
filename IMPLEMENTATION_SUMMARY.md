# AI Scientists Simulation - 実装サマリー

## 概要

research_plan.mdに基づき、2人のAI研究者が実際のGitHub PR/レビューシステムを通じて共同研究を行うシミュレーションを実装しました。

## 実装完了項目

### ✅ Phase 1: GitHub統合モジュール

**ファイル**: `github_manager.py`

**実装内容**:
- リポジトリの作成・初期化
- ブランチ作成・切り替え
- ファイルのコミット（新規・更新）
- Pull Request作成・取得
- レビューコメント追加（APPROVE/REQUEST_CHANGES/COMMENT）
- PRマージ・クローズ
- ファイル内容の取得
- PRの詳細情報取得（変更ファイル、diff含む）

**主要クラス**: `GitHubManager`

**特徴**:
- PyGitHub ライブラリを使用
- 完全な GitHub API 統合
- エラーハンドリングとリトライ機能

---

### ✅ Phase 2: Google Gemini統合

**ファイル**: `gemini_inference.py`

**実装内容**:
- Gemini API (google.generativeai) の呼び出し
- プロンプト構築（system + user prompt）
- トークン使用量の追跡（概算）
- コスト推定
- エラーハンドリングとリトライ
- 既存の `inference.py` と互換性のあるインターフェース

**主要関数**:
- `query_gemini()` - Gemini APIクエリ
- `query_model_gemini()` - 統一インターフェース
- `curr_cost_est()` - コスト推定
- `get_token_usage()` - トークン使用量取得

**特徴**:
- 複数のGeminiモデルに対応（gemini-pro, gemini-1.5-pro, gemini-1.5-flash）
- Temperature と max_tokens のカスタマイズ
- Safety filter エラーハンドリング

---

### ✅ Phase 3: 詳細ログシステム

**ファイル**: `simulation_logger.py`

**実装内容**:
- タイムスタンプ付きイベントログ
- 研究テーマ決定フェーズの記録
- 市民評価の完全記録（コメント、金額、理由）
- PRの作成・レビュー・マージ履歴
- **AI Scientistが与えたレビューの全文記録**
- **AI Scientistが受け取ったレビューの全文記録**
- GitHub操作履歴
- LLM API呼び出しログ
- 統計情報（承認率、やり直し回数など）

**出力形式**:
- JSON形式（`logs/simulation_log.json`）
- テキスト形式（`logs/simulation_log.txt`）
- リアルタイムコンソール出力

**主要クラス**: `SimulationLogger`

**記録される統計**:
- 総ステップ数
- PR総数・承認数・却下数
- 各科学者の進捗状況
- 市民報酬の合計・平均・分布
- ステージごとの所要時間
- 承認率・却下率

---

### ✅ Phase 4: 市民エージェント

**ファイル**: `citizen_agents.py`

**実装内容**:
- 10人の一般市民のペルソナ定義
- 各市民の独自の価値観と視点
- 研究テーマの評価
- 支援金額（1-1000円）の決定
- 意見・感想の生成

**市民リスト**:
1. **田中健太** (35歳, 営業職) - 実用性重視
2. **佐藤美香** (42歳, 主婦) - 家族・子供への影響
3. **山田誠** (54歳, 教師) - 教育的価値
4. **鈴木ユウキ** (27歳, 起業家) - イノベーション
5. **伊藤正男** (72歳, 退職者) - 社会貢献
6. **中村アヤ** (21歳, 大学生) - トレンド感
7. **小林サキ** (33歳, デザイナー) - クリエイティビティ
8. **吉田ケイコ** (45歳, 看護師) - 医療・健康
9. **渡辺タケシ** (52歳, 農家) - 地域社会
10. **高橋ヒロシ** (38歳, 工場作業員) - 雇用への影響

**主要クラス**: `CitizenAgent`

**特徴**:
- Gemini APIで評価を生成
- JSON形式でコメント・金額・理由を返す
- ペルソナに応じた自然な口調

---

### ✅ Phase 5: AI Scientistエージェント

**ファイル**: `ai_scientist_agents.py`

**実装内容**:
- **AgentLaboratoryの`BaseAgent`を継承**
- 研究ステージの実装（6段階）
- PR作成機能
- PRレビュー機能
- **コンテキスト保持機構**:
  - `self.history` - 全行動履歴
  - `self.pr_history` - 受け取ったレビュー履歴（全文）
  - `self.review_history` - **与えたレビュー履歴（全文・Approve/Reject両方）**
  - `self.peer_research_context` - 相手の研究進捗
  - `self.citizen_feedback` - 市民評価
- BaseAgentのメソッドを活用:
  - `inference()` - LLM推論（Gemini対応に改造）
  - `context()` - コンテキスト生成
  - `phase_prompt()` - フェーズ別プロンプト
  - `history` - 履歴管理

**研究ステージ**:
0. 研究テーマ決定
1. 仮説提案
2. 実験計画
3. 実験構築
4. 結果解釈
5. 論文執筆

**主要クラス**: `AIScientistAgent(BaseAgent)`

**重要機能**:
- `decide_research_theme()` - テーマ決定
- `create_stage_output()` - ステージ成果物作成
- `review_pr()` - PRレビュー実行
- `add_citizen_feedback()` - 市民評価の追加
- `add_pr_feedback()` - レビュー結果の追加
- `_build_review_context()` - **過去のレビュー履歴をコンテキスト化**

---

### ✅ Phase 6: シミュレーションワークフロー

**ファイル**: `research_simulation.py`

**実装内容**:
- シミュレーション全体の orchestration
- 初期化フェーズ（リポジトリ作成、ディレクトリ構造）
- 研究テーマ決定フェーズ
- 市民評価フェーズ
- メインループ（PR作成 → レビュー → 承認/却下）
- 終了条件の判定

**主要クラス**: `ResearchSimulation`

**ワークフロー**:
```
初期化
  ↓
テーマ決定（Scientist A & B）
  ↓
市民評価（10人 × 2テーマ）
  ↓
メインループ:
  Scientist A: ステージ実行 → PR作成
  Scientist B: レビュー → APPROVE/REJECT
  Scientist B: ステージ実行 → PR作成
  Scientist A: レビュー → APPROVE/REJECT
  ↓
両者が全ステージ完了で終了
```

**主要メソッド**:
- `initialize()` - GitHub初期化
- `phase_1_theme_decision()` - テーマ決定
- `phase_2_citizen_evaluation()` - 市民評価
- `conduct_research_stage()` - 研究ステージ実行
- `create_pr_for_stage()` - PR作成
- `review_pr()` - PRレビュー
- `run_simulation()` - メイン実行

---

### ✅ Phase 7: メインスクリプトと設定

**ファイル**: 
- `run_simulation.py` - メイン実行スクリプト
- `config.yaml` - 設定ファイル
- `config.example.yaml` - 設定ファイルのテンプレート
- `env_example.txt` - 環境変数のテンプレート

**run_simulation.py の機能**:
- コマンドライン引数のパース
- `.env` ファイルからの環境変数読み込み
- `config.yaml` からの設定読み込み
- **設定の優先順位**: コマンドライン > .env > config.yaml > デフォルト
- 必須パラメータの検証
- ユーザー確認プロンプト
- シミュレーション実行

**コマンドライン引数**:
- `--config` - 設定ファイルパス
- `--github-token` - GitHub token（.envより優先）
- `--gemini-api-key` - Gemini API key（.envより優先）
- `--research-topic` - 研究トピック
- `--max-steps` - 最大ステップ数
- `--repo-name` - リポジトリ名
- `--github-owner` - GitHubユーザー名
- `--log-dir` - ログディレクトリ
- `--no-console` - コンソール出力無効化
- `--model` - Geminiモデル選択

**config.yaml の構造**:
```yaml
research:
  topic: "研究トピック"
  max_steps: 100

github:
  repo_name: "リポジトリ名"
  owner: "GitHubユーザー名"

logging:
  log_dir: "./logs"
  console_output: true

agents:
  review_strictness: "medium"
  stage_timeout: 300

gemini:
  model: "gemini-pro"
  temperature: 0.7
  max_tokens: 2048
```

---

### ✅ Phase 8: 依存関係更新

**ファイル**: `requirements.txt`

**追加された依存関係**:
```
PyGithub>=2.1.1
google-generativeai>=0.3.0
python-dotenv>=1.0.0
```

**既存の依存関係**: PyYAML は既に含まれていた

---

## 追加ドキュメント

### ✅ README

**ファイル**: `AI_SCIENTISTS_SIMULATION_README.md`

**内容**:
- システム概要
- システム構成の詳細
- セットアップ手順
- 実行方法
- シミュレーションフロー
- ログとデータの説明
- トラブルシューティング
- カスタマイズ方法

### ✅ クイックスタートガイド

**ファイル**: `QUICK_START.md`

**内容**:
- 5分でできるセットアップ
- APIキーの取得方法（画面キャプチャ付き手順）
- 動作確認方法
- 最初のシミュレーション実行
- よくあるエラーと解決策

### ✅ テストスクリプト

**ファイル**: `test_simulation.py`

**機能**:
- モジュールインポートテスト
- 設定ファイル存在確認
- 環境変数チェック
- Gemini API接続テスト
- GitHub API接続テスト
- 市民エージェント作成テスト
- AI Scientistエージェント作成テスト
- ロガーテスト

**実行方法**:
```bash
python test_simulation.py
```

**出力**: 8つのテスト結果と総合評価

---

## 技術的特徴

### コンテキスト保持の実装

**重要**: 計画書の要求通り、すべてのレビューコメントとフィードバックをコンテキストとして保持

1. **`AIScientistAgent.review_history`**
   - 自分が相手に与えた**すべてのレビュー**を保存
   - Approve/Reject/Request changes **すべて**記録
   - 次のレビュー時に `_build_review_context()` で参照

2. **`AIScientistAgent.pr_history`**
   - 自分が受け取った**すべてのレビュー**を保存
   - 次の行動時に `context()` メソッドで参照

3. **`AIScientistAgent.citizen_feedback`**
   - 市民からの評価を永続的に保持
   - すべての研究ステージで参照可能

4. **`BaseAgent.history`**
   - AgentLaboratoryの機構を活用
   - すべての過去の行動を保持

### AgentLaboratory との統合

**継承構造**:
```
BaseAgent (AgentLaboratory)
    ↓
AIScientistAgent (新規実装)
```

**活用したメソッド**:
- `inference()` - Gemini用に改造
- `context()` - コンテキスト生成をオーバーライド
- `phase_prompt()` - 研究フェーズ用に実装
- `history` - 履歴管理機構をそのまま活用

**活用したツール**:
- `ArxivSearch` - 文献検索
- `execute_code` - コード実行
- （将来的に拡張可能）

---

## ディレクトリ構造

```
AgentLaboratory/
├── github_manager.py           # GitHub API統合
├── gemini_inference.py         # Gemini API統合
├── simulation_logger.py        # ログシステム
├── citizen_agents.py           # 市民エージェント
├── ai_scientist_agents.py      # AI Scientistエージェント
├── research_simulation.py      # ワークフロー管理
├── run_simulation.py           # メイン実行スクリプト
├── test_simulation.py          # テストスクリプト
├── config.yaml                 # 設定ファイル
├── config.example.yaml         # 設定テンプレート
├── env_example.txt             # 環境変数テンプレート
├── requirements.txt            # 依存関係（更新済み）
├── AI_SCIENTISTS_SIMULATION_README.md  # 詳細README
├── QUICK_START.md              # クイックスタート
├── IMPLEMENTATION_SUMMARY.md   # このファイル
└── logs/                       # ログディレクトリ（実行時に作成）
    ├── simulation_log.json
    └── simulation_log.txt
```

---

## 実行フロー

### 1. セットアップ

```bash
pip install -r requirements.txt
# .env ファイル作成
# config.yaml 編集
```

### 2. 動作確認

```bash
python test_simulation.py
```

### 3. シミュレーション実行

```bash
python run_simulation.py
```

### 4. 結果確認

- **GitHubリポジトリ**: `https://github.com/{owner}/{repo_name}`
  - PRとレビュー履歴
  - 研究成果物
  
- **ログファイル**: `logs/simulation_log.json`, `logs/simulation_log.txt`
  - 全イベントログ
  - 統計情報

---

## 計画書との対応

### ✅ 実装完了項目

| 計画書の項目 | 実装状況 | ファイル |
|------------|---------|---------|
| GitHub統合 | ✅ 完了 | `github_manager.py` |
| Gemini統合 | ✅ 完了 | `gemini_inference.py` |
| 詳細ログ | ✅ 完了 | `simulation_logger.py` |
| 市民エージェント（10人） | ✅ 完了 | `citizen_agents.py` |
| AI Scientistエージェント | ✅ 完了 | `ai_scientist_agents.py` |
| BaseAgent継承 | ✅ 完了 | `ai_scientist_agents.py` |
| コンテキスト保持 | ✅ 完了 | 全レビュー記録・参照 |
| シミュレーションワークフロー | ✅ 完了 | `research_simulation.py` |
| メインスクリプト | ✅ 完了 | `run_simulation.py` |
| 設定ファイル（YAML） | ✅ 完了 | `config.yaml` |
| 環境変数（.env） | ✅ 完了 | `env_example.txt` |
| コマンドライン引数 | ✅ 完了 | `run_simulation.py` |
| 依存関係更新 | ✅ 完了 | `requirements.txt` |
| ドキュメント | ✅ 完了 | README, QUICK_START |
| テストスクリプト | ✅ 完了 | `test_simulation.py` |

### 重要な実装詳細

#### ✅ コンテキスト保持（計画書の重要要件）

**計画書の要求**:
> マイステップの相手のscientistからのプルリクに対するレビューコメントもコンテキストに保持してください。approveとrejectどちらも場合でも。

**実装**:
- `AIScientistAgent.review_history` - **自分が与えたレビューを全て保存**
- `AIScientistAgent.pr_history` - 自分が受け取ったレビューを全て保存
- `_build_review_context()` - レビュー履歴をプロンプトに組み込み
- `context()` - すべてのコンテキストを統合

#### ✅ 市民エージェント（計画書の要求）

**計画書の要求**:
> 市民エージェントは、10人用意して、それぞれが異なるペルソナをもち、それぞれが異なる意見と報酬を持つようにしてください。

**実装**:
- 10人の一般市民（非研究者）
- 異なる職業・年齢・価値観
- 独自の評価基準と支援金額
- すべての発言と金額を詳細にログ

#### ✅ Gemini統合（計画書の要求）

**計画書の要求**:
> モデルはgoogle のgeminiでやりますのでそれにあわせてください。

**実装**:
- `gemini_inference.py` で完全対応
- 既存の `inference.py` と互換性のあるインターフェース
- すべてのエージェントでGemini使用

#### ✅ 設定の柔軟性（計画書の要求）

**計画書の要求**:
> コマンドライン引数は.envまたは、configファイルで指定できるようにしてください

**実装**:
- `.env` ファイル - APIキーなど機密情報
- `config.yaml` - その他の設定
- コマンドライン引数 - すべて上書き可能
- 優先順位: CLI > .env > config.yaml > defaults

---

## 次のステップ

### ユーザーが実行すべきこと

1. **セットアップ**
   ```bash
   cd AgentLaboratory
   pip install -r requirements.txt
   ```

2. **APIキー設定**
   - GitHub Personal Access Token 取得
   - Gemini API Key 取得
   - `.env` ファイル作成

3. **動作確認**
   ```bash
   python test_simulation.py
   ```

4. **シミュレーション実行**
   ```bash
   python run_simulation.py --max-steps 30
   ```

### 推奨される検証手順

1. テストスクリプトで全テストがパスすることを確認
2. 軽量版シミュレーション（30ステップ）を実行
3. GitHubリポジトリでPR/レビュー履歴を確認
4. ログファイルで詳細を確認
5. 問題なければ、フルシミュレーション（100ステップ）を実行

---

## まとめ

すべての実装が計画書通りに完了しました：

✅ **Phase 1-8**: すべて実装完了
✅ **GitHub統合**: 実際のGitHub API使用
✅ **市民エージェント**: 10人の多様なペルソナ
✅ **AI Scientist**: BaseAgent継承、コンテキスト保持
✅ **Gemini統合**: 全LLM推論でGemini使用
✅ **詳細ログ**: すべてのイベント・発言を記録
✅ **設定の柔軟性**: .env、config.yaml、CLI引数
✅ **ドキュメント**: README、クイックスタート、テストスクリプト

システムはテスト可能な状態です。ユーザーがAPIキーを設定すれば、即座にシミュレーションを実行できます。

