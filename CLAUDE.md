# Skill Genelator - プロジェクト設定

## 概要

GITEC 生成AIコンサルタント（しょーぱん）が自作した11のClaude Codeスキルと12体のサブエージェントのコレクション。

## エージェント一覧

| コマンド | エージェント | 担当スキル |
|---------|------------|-----------|
| `@skill-master` | スキルマスター（全スキル横断ナビゲーター） | 全スキル |
| `@brand-manager` | ブランドマネージャー | brand |
| `@marketing-strategist` | マーケティングストラテジスト | marketing-strategy |
| `@seo-analyst` | SEOアナリスト | marketing-seo |
| `@web-renewal-planner` | Webリニューアルプランナー | web-renewal-proposal |
| `@frontend-craftsman` | フロントエンド職人 | frontend-development-workflow |
| `@go-architect` | Goアーキテクト | go-cms |
| `@laravel-builder` | Laravelビルダー | laravel-cms |
| `@vba-maestro` | VBAマエストロ | excel-vba |
| `@ux-guardian` | UXガーディアン | ux-design |
| `@training-sensei` | トレーニング先生 | training-material |
| `@proposal-producer` | 提案書プロデューサー | gitec-proposal-generator |

## スキルコマンド体系

| コマンド | スキル名 |
|---------|---------|
| `/brand` | ブランドコンテキスト管理 |
| `/marketing-strategy` | マーケティング戦略策定 |
| `/marketing-seo` | SEO分析・コンテンツ計画 |
| `/web-renewal-proposal` | Webリニューアル提案 |
| `/frontend-development-workflow` | フロントエンド開発 |
| `/go-cms` | Go CMS構築 |
| `/laravel-cms` | Laravel CMS構築 |
| `/excel-vba` | VBAマクロ開発 |
| `/ux-design` | UX/UIデザイン |
| `/training-material` | 研修資料作成 |
| `/gitec-proposal-generator` | AI導入提案書生成 |

## プロジェクトルール

- スキルファイル（SKILL.md）の変更は慎重に行う
- エージェントの性格設定（キャラクター）は統一感を保つ
- `.skill` や `.zip` ファイルはGitにコミットしない
- クライアント固有情報はコミットしない
- 公開ガイドライン: `docs/skill-publishing-guide.md` を参照

## ファイル構成

```
.claude/
├── skills/       # 11スキル（SKILL.md + references等）
├── agents/       # 12エージェント（YAMLフロントマター + 本文）
docs/
├── agent-gallery.md           # エージェント紹介ギャラリー
└── skill-publishing-guide.md  # スキル公開ガイドライン
```
