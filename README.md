# Claude Code スキル & サブエージェント コレクション

しょーぱん（GITEC 生成AIコンサルタント）が実務で鍛えた12のスキルと、各スキルに特化した12体の個性的なサブエージェントを収録。ブランディングからCMS構築、提案書生成まで、AIコンサルタントの業務をカバーする。

---

## スキル一覧

| # | スキル名 | コマンド | 概要 |
|---|---------|---------|------|
| 1 | Brand | `/brand` | マーケティングセッションのブランドコンテキスト管理 |
| 2 | Marketing Strategy | `/marketing-strategy` | マーケティング戦略・ポジショニング・ペルソナ設計 |
| 3 | Marketing SEO | `/marketing-seo` | SEOキーワード調査・コンテンツプランニング・競合分析 |
| 4 | Web Renewal Proposal | `/web-renewal-proposal` | Webリニューアル提案の自動生成 |
| 5 | Frontend Development | `/frontend-development-workflow` | リキッドデザイン＋FLOCSS設計のフロントエンド開発 |
| 6 | Go CMS | `/go-cms` | Go言語でのフルスタックCMS構築 |
| 7 | Laravel CMS | `/laravel-cms` | LaravelでのセキュアなCMS自動構築 |
| 8 | Excel VBA | `/excel-vba` | VBAマクロ開発・Excel自動化 |
| 9 | UX Design | `/ux-design` | アクセシビリティファーストのUI/UX設計 |
| 10 | Training Material | `/training-material` | 生成AI研修・講義資料の自動生成 |
| 11 | GITEC Proposal | `/gitec-proposal-generator` | AI導入提案書の包括的自動生成 |

## サブエージェント（12体）

各スキルに特化した個性的なサブエージェントが、あなたの作業をサポートする。

| エージェント | キャラクター | 担当 |
|-------------|------------|------|
| Skill Master | 図書館司書的ナビゲーター | 全スキル横断 |
| Brand Manager | 几帳面な秘書官 | Brand |
| Marketing Strategist | 冷静な軍師 | Marketing Strategy |
| SEO Analyst | 誠実なデータ探偵 | Marketing SEO |
| Web Renewal Planner | 本音を引き出すコンサルタント | Web Renewal Proposal |
| Frontend Craftsman | 1pxにこだわる匠 | Frontend Development |
| Go Architect | Less is moreの設計者 | Go CMS |
| Laravel Builder | 手際のよい建築家 | Laravel CMS |
| VBA Maestro | Excelの指揮者 | Excel VBA |
| UX Guardian | アクセシビリティの番人 | UX Design |
| Training Sensei | わかりやすさの達人 | Training Material |
| Proposal Producer | 数字で動かすコンサルタント | GITEC Proposal |

詳細は [Agent Gallery](docs/agent-gallery.md) を参照。

## インストール方法

### 方法1: リポジトリごとクローン

```bash
git clone https://github.com/taira-s0422/skills.git
```

### 方法2: スキル単体をコピー

必要なスキルだけを `~/.claude/skills/` にコピー：

```bash
# 例: brand スキルをインストール
cp -r .claude/skills/brand ~/.claude/skills/
```

### 方法3: エージェントをコピー

```bash
# 例: skill-master エージェントをインストール
cp .claude/agents/skill-master.md ~/.claude/agents/
```

## 使い方

### スキルの起動

Claude Code で対応するスラッシュコマンドを入力：

```
/brand
/marketing-strategy
/frontend-development-workflow
```

### エージェントの呼び出し

Task ツールから対応するエージェントを指定：

```
@skill-master    → 最適なスキルを提案
@vba-maestro     → VBA開発をサポート
@go-architect    → Go CMS構築を支援
```

## ディレクトリ構成

```
.claude/
├── skills/           # 11スキル
│   ├── brand/
│   ├── marketing-strategy/
│   ├── marketing-seo/
│   ├── web-renewal-proposal/
│   ├── frontend-development-workflow/
│   ├── go-cms/
│   ├── laravel-cms/
│   ├── excel-vba/
│   ├── ux-design/
│   ├── training-material/
│   └── gitec-proposal-generator/
└── agents/           # 12エージェント
    ├── skill-master.md
    ├── brand-manager.md
    ├── marketing-strategist.md
    ├── seo-analyst.md
    ├── web-renewal-planner.md
    ├── frontend-craftsman.md
    ├── go-architect.md
    ├── laravel-builder.md
    ├── vba-maestro.md
    ├── ux-guardian.md
    ├── training-sensei.md
    └── proposal-producer.md
docs/
├── agent-gallery.md        # エージェント紹介ギャラリー
└── skill-publishing-guide.md  # スキル公開ガイドライン
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照。

## 作者

**しょーぱん** / GITEC 生成AIコンサルタント
- GitHub: [@taira-s0422](https://github.com/taira-s0422)
