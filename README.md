# AI Scientists Simulation

<p align="center">
  <strong>2つのAI scientistsがGitHub PR/reviewプロセスを通じて共同研究を行うシミュレーションシステム</strong>
</p>

## 📖 概要

**AI Scientists Simulation**は、2つの独立したAI scientistsが実際のGitHubリポジトリ上でプルリクエストとコードレビューを通じて協力しながら研究を進めるシミュレーションシステムです。

### 主な特徴

- **2つの独立したAI scientist**: それぞれ異なるGitHubアカウントで動作し、本物の研究者のように振る舞います
- **6段階の研究プロセス**: テーマ決定 → 仮説 → 実験計画 → 実装 → 結果解釈 → 論文執筆
- **GitHub統合**: 実際のPR作成、コードレビュー、承認/却下、マージを実行
- **市民エージェント評価**: 5人の多様なペルソナを持つ市民エージェントが研究テーマを評価し、報酬を配分
- **詳細なログ記録**: すべての意思決定、PR、レビュー、エラーを記録
- **Google Gemini API**: 最新のLLMを活用した高度な推論能力

## 🎯 システムの仕組み

```
初期化
  ↓
テーマ決定フェーズ
  ├─ Scientist A: テーマ提案 → PR作成
  ├─ Scientist B: テーマ提案 → PR作成
  └─ 市民エージェント: 各テーマを評価・報酬配分
  ↓
メイン研究ループ (各ステージで繰り返し)
  ├─ Scientist A: ステージ完了 → PR作成
  ├─ Scientist B: レビュー → 承認/却下
  ├─ (承認の場合) マージ
  ├─ Scientist B: ステージ完了 → PR作成
  ├─ Scientist A: レビュー → 承認/却下
  └─ (承認の場合) マージ
  ↓
完了 (すべてのステージが完了)
```

## 🚀 クイックスタート

### 前提条件

- **Python 3.10以上**
- **Git**
- **2つのGitHubアカウント**
  - 個人アカウント (Scientist A用)
  - 機械アカウント (Scientist B用) - [GitHubの規約](https://docs.github.com/ja/github/site-policy/github-terms-of-service)で許可されています
- **Google Gemini API key** - [こちらから取得](https://makersuite.google.com/app/apikey)

### インストール

1. **リポジトリのクローン**

```bash
git clone https://github.com/your-username/AI-scientists-simulation.git
cd AI-scientists-simulation/AgentLaboratory
```

2. **Python仮想環境の作成と有効化**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **依存パッケージのインストール**

```bash
pip install -r requirements.txt
```

### GitHubセットアップ

#### 1. 2つのGitHubアカウントの準備

- **Scientist A**: 既存の個人アカウント（例: `chikaranabla`）
- **Scientist B**: 新規作成した機械アカウント（例: `chikaraoe-en`）

#### 2. Personal Access Token (PAT) の作成

両方のアカウントで以下の手順を実行：

1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" をクリック
3. Note: `AI Scientists Simulation` など
4. Expiration: 適切な期限を設定
5. **Scopes**: `repo` (フルコントロール) にチェック
6. "Generate token" をクリック
7. **トークンをコピーして保存**（再表示できません）

#### 3. コラボレーターの追加

Scientist A (リポジトリオーナー) のアカウントで：

1. 後で作成されるリポジトリ（例: `ai-scientists-research`）の Settings → Collaborators
2. "Add people" をクリック
3. Scientist B のユーザー名を入力して招待
4. Scientist B のアカウントで招待を承諾

**注意**: リポジトリは初回実行時に自動作成されます。作成後にコラボレーターを追加してください。

### 環境変数の設定

1. **`.env` ファイルの作成**

```bash
cp env_example.txt .env
```

2. **`.env` ファイルの編集**

```env
# Scientist A's GitHub Account Token
GITHUB_TOKEN_A=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Scientist B's GitHub Account Token
GITHUB_TOKEN_B=ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

# Repository Owner (Scientist A's username)
GITHUB_OWNER=chikaranabla

# Google Gemini API Key
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### config.yaml の設定

研究トピックやその他の設定を `config.yaml` で編集：

```yaml
research:
  topic: "自然言語処理における感情分析の改良"
  max_steps: 100

github:
  repo_name: "ai-scientists-research"
  owner: "chikaranabla"  # GITHUB_OWNERで上書き可能

logging:
  log_dir: "./logs"
  console_output: true

gemini:
  model: "gemini-2.0-flash-lite"
  temperature: 0.7
  max_tokens: 2048
```

### 実行

```bash
python run_simulation.py
```

設定を確認してから `y` を入力してシミュレーションを開始します。

## 📁 ディレクトリ構造

```
AgentLaboratory/
├── run_simulation.py          # メイン実行スクリプト
├── research_simulation.py     # シミュレーション管理
├── github_manager.py          # GitHub API統合
├── ai_scientist_agents.py     # AI scientistエージェント
├── citizen_agents.py          # 市民エージェント
├── simulation_logger.py       # ログ記録
├── inference.py               # LLM推論
├── config.yaml                # 設定ファイル
├── .env                       # 環境変数（要作成）
├── env_example.txt            # 環境変数テンプレート
├── requirements.txt           # 依存パッケージ
├── QUICK_START.md            # 詳細なクイックスタートガイド
├── README.md                 # このファイル
└── logs/                     # シミュレーションログ（自動生成）
    ├── simulation_log.json
    └── simulation_log.txt
```

## 🔬 研究ステージ

シミュレーションは以下の6つのステージで構成されます：

1. **theme_decision**: 研究テーマの決定と具体化
2. **hypothesis**: 具体的な仮説の立案
3. **experiment_plan**: 実験計画の策定
4. **experiment_implementation**: 実験コードの実装
5. **results_interpretation**: 結果の解釈と分析
6. **paper_writing**: 論文の執筆

各ステージで：
- Scientistが成果物を作成してPRを提出
- もう一方のScientistがレビュー
- 承認されればマージ、却下されれば修正して再提出

## 👥 市民エージェント

5人の多様なペルソナを持つ市民エージェントが研究テーマを評価：

1. **佐藤美咲**: 30代の会社員、実用性重視
2. **田中健太**: 20代の大学生、技術的興味
3. **鈴木花子**: 60代の主婦、社会への影響
4. **山田太郎**: 田舎の農家、分かりやすさ
5. **高橋ヒロシ**: 工場作業員、新技術への期待と不安

各市民は研究テーマに対して：
- コメントを投稿
- 報酬額を決定（100円〜10,000円）
- 推論プロセスを説明

## 📊 ログとモニタリング

シミュレーション実行後、`logs/` ディレクトリに以下が保存されます：

- **simulation_log.json**: 構造化されたログデータ
- **simulation_log.txt**: 人間が読みやすい形式のログ

ログには以下の情報が含まれます：
- すべてのPR作成とレビュー
- 市民エージェントの評価
- LLMの推論プロセス
- エラーと警告
- タイムスタンプ付きイベント

## 🛠️ トラブルシューティング

### GitHub API 422エラー: "Can not request changes on your own pull request"

**原因**: 両方のScientistが同じGitHubアカウントを使用している

**解決策**: 2つの異なるGitHubアカウントを使用し、`.env` に両方のトークンを設定

### GitHub API Rate Limit

**症状**: "API rate limit exceeded" エラー

**解決策**:
- 認証済みリクエストは1時間に5,000回まで
- 待つか、別のアカウントを使用
- [レート制限の確認](https://api.github.com/rate_limit)

### Gemini API エラー

**症状**: "Invalid API key" や認証エラー

**解決策**:
- API keyが正しく設定されているか確認
- [Gemini API Console](https://makersuite.google.com/app/apikey)で確認
- APIが有効化されているか確認

### コラボレーターの権限エラー

**症状**: Scientist BがPRを作成できない

**解決策**:
1. Scientist Bがリポジトリのコラボレーターとして追加されているか確認
2. Scientist Bが招待を承諾したか確認
3. GITHUB_TOKEN_Bに `repo` スコープがあるか確認

## ⚙️ 高度な設定

### コマンドライン引数

```bash
# カスタム設定ファイルを使用
python run_simulation.py --config custom_config.yaml

# 研究トピックを上書き
python run_simulation.py --research-topic "機械学習の解釈可能性"

# 最大ステップ数を変更
python run_simulation.py --max-steps 50

# 異なるGeminiモデルを使用
python run_simulation.py --model "gemini-1.5-pro"

# すべてのオプションを表示
python run_simulation.py --help
```

### サポートされているGeminiモデル

- `gemini-2.0-flash-lite` (デフォルト、高速)
- `gemini-2.0-flash-exp` (実験的)
- `gemini-1.5-pro` (高精度)
- `gemini-1.5-flash` (バランス型)

## 📜 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。

## 🙏 謝辞

このプロジェクトは[Agent Laboratory](https://github.com/SamuelSchmidgall/AgentLaboratory)プロジェクトのコードベースを基に開発されました。元のプロジェクトの作成者とコントリビューターに感謝します。

元のAgent Laboratory論文:
```bibtex
@misc{schmidgall2025agentlaboratoryusingllm,
      title={Agent Laboratory: Using LLM Agents as Research Assistants}, 
      author={Samuel Schmidgall and Yusheng Su and Ze Wang and Ximeng Sun and Jialian Wu and Xiaodong Yu and Jiang Liu and Zicheng Liu and Emad Barsoum},
      year={2025},
      eprint={2501.04227},
      archivePrefix={arXiv},
      primaryClass={cs.HC},
      url={https://arxiv.org/abs/2501.04227}, 
}
```

## 📬 連絡先

質問やフィードバックがある場合は、Issueを作成してください。

## 🌟 コントリビューション

プルリクエストを歓迎します！改善のアイデアがある場合は：

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを開く

## 📝 更新履歴

### Version 1.0.0
- 初回リリース
- 2つのGitHubアカウントによるマルチエージェントシミュレーション
- 市民エージェント評価システム
- 6段階の研究プロセス
- 完全なGitHub統合
- Google Gemini API統合
- 詳細なログ記録

---

**Happy Researching! 🔬🤖**
