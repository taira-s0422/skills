---
name: laravel-cms
description: LaravelでセキュアなCMSを構築するスキル。記事投稿、ページ管理、メディア管理、ユーザー権限管理を含む。静的HTMLテンプレートをBlade化してCMS化するワークフローをサポート。「Laravel CMSを作成」「CMSを構築」「/laravel-cms」で起動。
---

# Laravel CMS Builder - 自動構築スキル

このスキルが起動されたら、**ユーザーの確認後、以下を全て自動で作成する**。

## 起動時の確認事項

ユーザーに以下を確認：

1. **プロジェクトタイプ**
   - 1: 新規CMSを1から構築
   - 2: 既存プロジェクトに追加

2. **機能選択**
   - 1: 基本機能のみ（記事・ページ・メディア・ユーザー管理）
   - 2: 全機能（基本 + コメント・お問い合わせ・SEO）

確認後、**自動で全ファイルを作成開始する**。途中で止めない。

---

## 重要: Laravel 12 制約（必ず守る）

### PHP要件
- Laravel 12はPHP 8.4以上が必須
- MAMPのPHP（8.2）では動作しない
- `php artisan serve` で起動（MAMPは使わない）

### コントローラー認可
以下は**使用禁止**（Laravel 11/12で動作しない）：
- ❌ `$this->middleware()`
- ❌ `$this->authorizeResource()`

代わりに**各メソッドで個別認可**：
```php
public function index() {
    $this->authorize('viewAny', Post::class);
}
public function edit(Post $post) {
    $this->authorize('update', $post);
}
```

### ベースController（必須）
```php
// app/Http/Controllers/Controller.php
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

abstract class Controller
{
    use AuthorizesRequests;
}
```

---

## 自動作成するファイル一覧

### Phase 1: プロジェクト初期化
```bash
composer create-project laravel/laravel [project-name]
cd [project-name]
composer require laravel/sanctum spatie/laravel-permission intervention/image-laravel spatie/laravel-activitylog
composer require --dev phpstan/phpstan
php artisan vendor:publish --provider="Spatie\Permission\PermissionServiceProvider"
php artisan vendor:publish --provider="Spatie\Activitylog\ActivitylogServiceProvider" --tag="activitylog-migrations"
```

### Phase 2: ベースController修正
`app/Http/Controllers/Controller.php` に `AuthorizesRequests` を追加。

### Phase 3: マイグレーション（全て作成）
- create_categories_table
- create_tags_table
- create_media_table
- create_posts_table（post_tag中間テーブル含む）
- create_pages_table
- create_comments_table
- create_contacts_table
- create_seo_settings_table
- create_site_settings_table

### Phase 4: モデル（全て作成）
- User.php（HasRoles, CausesActivity追加）
- Post.php（スコープ: published, draft, scheduled）
- Page.php（スコープ: published, root）
- Category.php
- Tag.php
- Media.php
- Comment.php（スコープ: approved, pending）
- Contact.php（スコープ: unread, read）
- SeoSetting.php
- SiteSetting.php

### Phase 5: ポリシー
- PostPolicy.php
- PagePolicy.php

### Phase 6: シーダー
- RolePermissionSeeder.php（super-admin, admin, editor, author + 全権限）
- AdminUserSeeder.php（admin@example.com / password）
- DatabaseSeeder.php（上記を呼び出し）

### Phase 7: FormRequest
- StorePostRequest.php
- UpdatePostRequest.php
- StorePageRequest.php
- UpdatePageRequest.php
- MediaUploadRequest.php

### Phase 8: 管理画面コントローラー（全メソッドに$this->authorize()付き）
- DashboardController.php
- PostController.php
- PageController.php
- CategoryController.php
- TagController.php
- MediaController.php
- CommentController.php
- ContactController.php
- UserController.php
- SettingController.php

### Phase 9: フロントコントローラー
- HomeController.php
- PostController.php（Front用）
- PageController.php（Front用）
- ContactController.php（Front用）

### Phase 10: ルート設定
`routes/web.php` を完全に書き換え：
- フロントエンド: /, /blog, /blog/{slug}, /contact, /page/{slug}
- 管理画面: /admin/* （全リソースルート）

### Phase 11: 管理画面ビュー（全て作成）
```
resources/views/
├── layouts/admin.blade.php
├── auth/login.blade.php
└── admin/
    ├── dashboard.blade.php
    ├── posts/index.blade.php, create.blade.php, edit.blade.php
    ├── pages/index.blade.php, create.blade.php, edit.blade.php, show.blade.php
    ├── categories/index.blade.php, create.blade.php, edit.blade.php
    ├── tags/index.blade.php, create.blade.php, edit.blade.php
    ├── media/index.blade.php
    ├── comments/index.blade.php, show.blade.php, edit.blade.php
    ├── contacts/index.blade.php, show.blade.php
    ├── users/index.blade.php, create.blade.php, edit.blade.php
    └── settings/index.blade.php, seo.blade.php
```

### Phase 12: フロントエンドビュー（全て作成）
```
resources/views/
├── layouts/front.blade.php
└── front/
    ├── home.blade.php
    ├── contact.blade.php
    ├── posts/index.blade.php, show.blade.php
    └── pages/default.blade.php
```

### Phase 13: AppServiceProvider設定
- Gate::before でsuper-admin全権限
- ポリシー登録

### Phase 14: 最終処理
```bash
php artisan migrate
php artisan db:seed
php artisan cache:clear
php artisan config:clear
php artisan route:clear
```

---

## 完了後の報告

全て作成完了したら、以下を報告：

```
✅ Laravel CMS構築完了

【アクセス方法】
php artisan serve

- フロント: http://127.0.0.1:8000/
- 管理画面: http://127.0.0.1:8000/admin
- ログイン: admin@example.com / password

【作成したファイル数】
- マイグレーション: X個
- モデル: X個
- コントローラー: X個
- ビュー: X個

【注意】
MAMPではなく `php artisan serve` を使用してください（PHP 8.4必須）
```

---

## 詳細リファレンス

実装の詳細が必要な場合は以下を参照：
- [references/database.md](references/database.md) - DB設計
- [references/features.md](references/features.md) - 機能実装
- [references/security.md](references/security.md) - セキュリティ
- [references/template-conversion.md](references/template-conversion.md) - テンプレート変換
- [references/customization.md](references/customization.md) - カスタマイズ
