# しょーぱんの Claude Code スキル

GITEC 生成AIコンサルタント（しょーぱん）が作成した Claude Code 用スキルとサブエージェントを公開しています。

## スキル一覧

| スキル名 | コマンド | 概要 |
|---------|---------|------|
| Brand | `/brand` | マーケティングセッションのブランドコンテキスト管理 |
| Marketing Strategy | `/marketing-strategy` | マーケティング戦略・ポジショニング・ペルソナ設計 |
| Marketing SEO | `/marketing-seo` | SEOキーワード調査・コンテンツプランニング・競合分析 |
| Web Renewal Proposal | `/web-renewal-proposal` | Webリニューアル提案の自動生成 |
| Frontend Development | `/frontend-development-workflow` | リキッドデザイン＋FLOCSS設計のフロントエンド開発 |
| Go CMS | `/go-cms` | Go言語でのフルスタックCMS構築 |
| Laravel CMS | `/laravel-cms` | LaravelでのセキュアなCMS自動構築 |
| Excel VBA | `/excel-vba` | VBAマクロ開発・Excel自動化 |
| UX Design | `/ux-design` | アクセシビリティファーストのUI/UX設計 |
| Training Material | `/training-material` | 生成AI研修・講義資料の自動生成 |
| GITEC Proposal | `/gitec-proposal-generator` | AI導入提案書の包括的自動生成 |
| Skill Security Checker | `/skill-security-checker` | スキルの安全性を自動検査するセキュリティチェッカー |

## サブエージェント

各スキルに特化した12体のサブエージェントも同梱しています。詳細は [Agent Gallery](docs/agent-gallery.md) を参照。

## インストール方法

### スキルをコピー

```bash
git clone https://github.com/taira-s0422/skills.git
cp -r skills/.claude/skills/brand ~/.claude/skills/
```

### エージェントをコピー

```bash
cp skills/.claude/agents/skill-master.md ~/.claude/agents/
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照。

## 作者

**しょーぱん** / GITEC 生成AIコンサルタント
