# AI Scientists Simulation - クイックスタートガイド

このガイドでは、AI Scientists Simulationを最短で起動・テストする手順を説明します。

## 前提条件

- Python 3.8以上
- GitHubアカウント
- Google Gemini APIアカウント

## セットアップ（5分）

### 1. 依存関係のインストール

```bash
cd AgentLaboratory
pip install -r requirements.txt
```

### 2. API キーの取得

#### GitHub Personal Access Token

1. https://github.com/settings/tokens にアクセス
2. "Generate new token (classic)" をクリック
3. Token nameを入力（例: "AI Scientists Simulation"）
4. Expiration（有効期限）を選択（例: 30 days）
5. **Scopes**で以下を選択:
   - ✅ **repo** (Full control of private repositories) - すべてのサブ項目にチェック
6. "Generate token" をクリック
7. **トークンをコピー**（このページを離れると二度と表示されません！）

#### Google Gemini API Key

1. https://makersuite.google.com/app/apikey にアクセス
2. "Create API key" をクリック
3. プロジェクトを選択（または新規作成）
4. **APIキーをコピー**

### 3. 環境設定ファイルの作成

#### `.env` ファイルの作成

```bash
# AgentLaboratory ディレクトリで実行
cat > .env << 'EOF'
GITHUB_TOKEN=あなたのGitHubトークン
GEMINI_API_KEY=あなたのGemini APIキー
GITHUB_OWNER=あなたのGitHubユーザー名
EOF
```

または、手動で `.env` ファイルを作成:

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=your-github-username
```

⚠️ **重要**: `.env` ファイルは絶対にGitにコミットしないでください！

#### `config.yaml` の編集

`config.yaml` を開いて、`owner` を自分のGitHubユーザー名に変更:

```yaml
github:
  repo_name: "ai-scientists-research"
  owner: "your-github-username"  # ← ここを変更
```

## 動作確認（2分）

システムが正しくセットアップされているか確認:

```bash
python test_simulation.py
```

### 期待される出力

```
================================================================================
AI SCIENTISTS SIMULATION - SYSTEM VALIDATION
================================================================================

================================================================================
TEST 1: Module Imports
================================================================================
✓ PyGithub imported successfully
✓ google-generativeai imported successfully
✓ PyYAML imported successfully
✓ python-dotenv imported successfully
✓ github_manager.py imported successfully
✓ gemini_inference.py imported successfully
...

================================================================================
TEST SUMMARY
================================================================================
✓ PASS: Module Imports
✓ PASS: Configuration Files
✓ PASS: Environment Variables
✓ PASS: Gemini API
✓ PASS: GitHub API
✓ PASS: Citizen Agents
✓ PASS: AI Scientists
✓ PASS: Logger

Total: 8/8 tests passed

✓ All tests passed! System is ready for simulation.
```

すべてのテストが通れば準備完了です！

## シミュレーション実行（10-30分）

### 最初のシミュレーション（軽量版）

```bash
python run_simulation.py --max-steps 30
```

このコマンドは：
- 最大30ステップの軽量シミュレーションを実行
- 新しいGitHubリポジトリを作成
- 2人のAI Scientists間でPR/レビューのやり取りを実行
- 10人の市民による研究評価を実施
- すべてのログを `logs/` に保存

### 実行確認

プログラムが以下を表示したら、`y` を入力して続行:

```
Proceed with simulation? [y/N]: y
```

### 実行中の表示例

```
================================================================================
INITIALIZING SIMULATION
================================================================================
Repository initialized successfully!

================================================================================
PHASE 1: RESEARCH THEME DECISION
================================================================================
Scientist A is deciding research theme...
Scientist A's theme: 深層学習を用いた感情認識システムの開発

Scientist B is deciding research theme...
Scientist B's theme: 自然言語処理における文脈理解の改善

================================================================================
PHASE 2: CITIZEN EVALUATION
================================================================================
Citizens are evaluating the research themes...
  田中健太 is evaluating...
    Scientist A: 450円, Scientist B: 320円
  佐藤美香 is evaluating...
    Scientist A: 280円, Scientist B: 510円
  ...

================================================================================
MAIN RESEARCH LOOP
================================================================================
...
```

### 完了

シミュレーション完了後、以下を確認できます:

1. **GitHubリポジトリ**
   ```
   https://github.com/あなたのユーザー名/ai-scientists-research
   ```
   - PRとレビューの履歴
   - 研究成果物（仮説、実験計画、コードなど）

2. **ログファイル**
   ```
   logs/simulation_log.json  # 構造化されたログ
   logs/simulation_log.txt   # 可読性の高いログ
   ```

## トラブルシューティング

### エラー: `ModuleNotFoundError`

**解決策**: 依存関係を再インストール
```bash
pip install -r requirements.txt
```

### エラー: `Bad credentials` (GitHub)

**原因**: GitHub tokenが無効または期限切れ

**解決策**:
1. 新しいtokenを生成
2. `.env` ファイルの `GITHUB_TOKEN` を更新

### エラー: `API key not valid` (Gemini)

**原因**: Gemini APIキーが無効

**解決策**:
1. https://makersuite.google.com/app/apikey でキーを確認
2. `.env` ファイルの `GEMINI_API_KEY` を更新

### エラー: `Repository already exists`

**原因**: 同名のリポジトリが既に存在

**解決策1**: 既存のリポジトリを削除してから再実行

**解決策2**: 別の名前を指定
```bash
python run_simulation.py --repo-name ai-scientists-test-2
```

### シミュレーションが遅い

**原因**: Gemini APIの呼び出しには時間がかかります

**対策**:
- `--max-steps` を減らす（例: `--max-steps 20`）
- より高速なモデルを使用（`--model gemini-1.5-flash`）

### GitHub API Rate Limit

**原因**: 1時間に5000リクエストの制限

**対策**:
- しばらく待ってから再実行
- `test_simulation.py` でrate limitを確認:
  ```bash
  python test_simulation.py
  ```

## 次のステップ

### カスタマイズ

研究トピックを変更して実行:

```bash
python run_simulation.py --research-topic "強化学習による自動運転技術"
```

詳細な設定を変更:

```bash
# config.yaml を編集
nano config.yaml

# カスタム設定で実行
python run_simulation.py --config config.yaml
```

### ログ分析

ログファイルからインサイトを抽出:

```bash
# JSON形式で統計を表示
python -m json.tool logs/simulation_log.json | grep -A 20 "statistics"

# PRの承認率を確認
python -m json.tool logs/simulation_log.json | grep "approval_rate"
```

### 詳細ドキュメント

完全なドキュメントは `AI_SCIENTISTS_SIMULATION_README.md` を参照してください。

## ヘルプ

コマンドライン引数のヘルプを表示:

```bash
python run_simulation.py --help
```

---

**問題が解決しない場合**: 
- `test_simulation.py` の出力を確認
- エラーメッセージの全文をコピー
- `logs/simulation_log.txt` でエラーの詳細を確認

