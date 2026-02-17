# Skill Security Checker

Claude Code スキルの安全性をインストール前に検査するセキュリティチェッカー。

Pythonによるパターン検出（8カテゴリ）と、Claudeによるセマンティック分析を組み合わせたハイブリッド方式。

## 動作要件

- Python 3.8 以上
- 外部パッケージ不要（標準ライブラリのみ）

## インストール

```bash
cp -r skill-security-checker ~/.claude/skills/
```

## 使い方

### Claude Code から実行

```
/skill-security-checker <対象パス>
```

### セーフインストール（推奨）

スキャンしてSAFEの場合のみ自動インストール:

```bash
python3 ~/.claude/skills/skill-security-checker/scripts/skill_scanner.py <対象パス> --install
```

| 判定 | --install の動作 |
|------|-----------------|
| SAFE | `~/.claude/skills/` に自動コピー |
| WARNING | インストール中断。手動確認を促す |
| DANGER | インストール拒否 |

`~/.claude/skills/` に直接コピーするとClaude Codeが即座にスキルを読み込むため、**必ずスキャンしてからインストールすること**。

### スキャンのみ

```bash
python3 ~/.claude/skills/skill-security-checker/scripts/skill_scanner.py <対象パス>
python3 ~/.claude/skills/skill-security-checker/scripts/skill_scanner.py <対象パス> --json
```

対象パスには以下を指定可能:

- ディレクトリパス（スキルフォルダ）
- `.skill` ファイル（ZIP形式）
- `.zip` ファイル

## 検査内容

### 自動スキャン（Python）

8カテゴリの危険パターンを正規表現で検出:

1. 認証情報の露出（APIキー、トークン、秘密鍵）
2. 危険コマンド（rm -rf、sudo、eval、curl|sh）
3. データ窃取（環境変数、外部送信）
4. パストラバーサル（../../、システムファイル）
5. 権限バイパス（sandbox無効化、bypassPermissions）
6. プロンプトインジェクション（指示の上書き、ジェイルブレイク）
7. 難読化（Base64、Hex、文字コード連結）
8. サプライチェーン（不審なパッケージインストール）

### セマンティック分析（Claude）

自動スキャン後、Claudeが以下を追加分析:

- 意図の一貫性（説明と実際のコードの動作が一致しているか）
- 隠れた危険性（コメントアウト、変数名偽装、条件分岐内の不審コード）
- AI/エージェント特有の脅威（設定改ざん、プロンプト汚染）
- 社会工学的手口（偽の緊急性、過度な権限要求）

## ライセンス

MIT License
