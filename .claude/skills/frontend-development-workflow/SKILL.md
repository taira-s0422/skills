---
name: frontend-development-workflow
description: リキッドデザインとFLOCSS設計に基づいた体系的なフロントエンド開発を支援。参考サイトの忠実な再現からオリジナルデザインの展開まで、6フェーズのワークフローでプロジェクトを進行する。使用タイミング：(1) 参考サイトを再現したい時、(2) FLOCSSでCSS設計したい時、(3) リキッドデザインで実装したい時、(4) LPやコーポレートサイトを制作する時、(5)「フロントエンド開発」「サイト制作」「コーディング」などのリクエスト時。
---

# Frontend Development Workflow

リキッドデザイン + FLOCSS設計に基づく体系的なフロントエンド開発ワークフロー。

## 技術仕様（必読）

### リキッドデザイン
- **ブレークポイント**: 767px
- **基準フォントサイズ**: `html { font-size: 62.5%; }` → 1rem = 10px
- **可変幅**: ビューポート幅に応じて流動的にスケール

### FLOCSS命名規則
| レイヤー | 接頭辞 | 例 |
|---------|--------|-----|
| Foundation | なし | `html`, `body`, `:root` |
| Layout | `l-` | `l-header`, `l-footer`, `l-container` |
| Component | `c-` | `c-button`, `c-card`, `c-heading` |
| Project | `p-` | `p-top`, `p-top__hero`, `p-about` |
| Utility | `u-` | `u-mt-10`, `u-text-center` |

詳細は [references/flocss-guide.md](references/flocss-guide.md) を参照。

---

## 6フェーズワークフロー

### Phase 1: 要件定義・分析
1. 参考サイトのキャプチャ画像を確認
2. セクションごとに詳細分析（配色、タイポグラフィ、レイアウト）
3. サイトマップ確認
4. TOPページ構成定義

**出力**: デザイン分析レポート（テンプレートは [references/phase-templates.md](references/phase-templates.md)）

### Phase 2: デザイン提案
1. 3案を作成:
   - 案A: 参考サイトに忠実（90%再現）
   - 案B: エッセンスを活かしつつモダン化
   - 案C: 独自性を強調
2. ユーザーに提示し選択を得る
3. 最終デザイン確定

**出力**: 確定デザイン仕様書

### Phase 3: 設計
1. コンポーネント一覧作成（FLOCSS分類）
2. ディレクトリ構造設計
3. 再利用計画

**出力**: コンポーネント一覧表（テンプレートは [references/phase-templates.md](references/phase-templates.md)）

### Phase 4: 実装（参考サイト再現）
1. セクション単位で実装（ヘッダー → ヒーロー → コンテンツ → フッター）
2. 各セクションで:
   - セマンティックHTML構築
   - FLOCSSクラス命名
   - CSSスタイリング
   - リキッドデザイン対応確認
3. 参考サイトとの精度確認・調整

**実装ガイドライン**: [references/implementation.md](references/implementation.md)

### Phase 5: オリジナル調整
1. ブランド独自の要素を追加（ロゴ、カラー調整、独自コンテンツ）
2. タイポグラフィ・アニメーション・視覚的ディテール強化
3. 全体の一貫性・パフォーマンス・アクセシビリティ確認

### Phase 6: ページ展開
1. 下層ページの構成MD確認
2. 既存コンポーネント再利用してページ構築
3. ページ固有スタイル追加（`p-ページ名`）
4. レスポンシブ対応確認

---

## クイックスタート

### 新規プロジェクト開始
```bash
# プロジェクト初期化スクリプトを実行
python3 scripts/init_project.py <project-name> --path <output-directory>
```

または [assets/template/](assets/template/) からコピー。

### 既存プロジェクトにFLOCSS導入
1. [references/flocss-guide.md](references/flocss-guide.md) のディレクトリ構造を参照
2. 既存CSSをFLOCSSレイヤーに分類
3. 命名規則に従ってリファクタリング

---

## リソース

### scripts/
- `init_project.py`: FLOCSS構造のプロジェクトを初期化

### references/
- `flocss-guide.md`: FLOCSS詳細ガイド・命名規則・ディレクトリ構造
- `phase-templates.md`: 各フェーズの出力テンプレート集
- `implementation.md`: 実装ガイドライン・ベストプラクティス・トラブルシューティング

### assets/
- `template/`: FLOCSS構造のプロジェクトテンプレート（HTML/CSS）
