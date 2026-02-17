# セキュリティ実装ガイド

## 目次
1. [CSRF対策](#csrf対策)
2. [XSS対策](#xss対策)
3. [SQLインジェクション対策](#sqlインジェクション対策)
4. [認証・認可](#認証認可)
5. [ファイルアップロード](#ファイルアップロード)
6. [セキュリティヘッダー](#セキュリティヘッダー)
7. [監査ログ](#監査ログ)
8. [その他のセキュリティ対策](#その他のセキュリティ対策)

---

## CSRF対策

Laravelは標準でCSRF保護を提供。

### フォームでの使用

```blade
<form method="POST" action="/posts">
    @csrf
    <!-- フォーム内容 -->
</form>
```

### Ajax/APIでの使用

```javascript
// metaタグから取得
const token = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/posts', {
    method: 'POST',
    headers: {
        'X-CSRF-TOKEN': token,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### レイアウトにmetaタグ追加

```blade
<head>
    <meta name="csrf-token" content="{{ csrf_token() }}">
</head>
```

---

## XSS対策

### Bladeでのエスケープ

```blade
{{-- 自動エスケープ（推奨） --}}
{{ $user->name }}

{{-- 生HTML出力（信頼できるコンテンツのみ） --}}
{!! $post->content !!}
```

### HTMLを許可する場合のサニタイズ

```php
// config/purifier.php でHTMLPurifierを設定
// composer require mews/purifier

use Mews\Purifier\Facades\Purifier;

$cleanHtml = Purifier::clean($dirtyHtml);
```

### JavaScript内でのエスケープ

```blade
<script>
    const userName = @json($user->name);
</script>
```

---

## SQLインジェクション対策

### Eloquent ORM使用（推奨）

```php
// 安全：Eloquentが自動エスケープ
$posts = Post::where('status', $status)->get();

// 安全：プレースホルダ使用
$posts = Post::whereRaw('status = ?', [$status])->get();
```

### 危険なパターン（避ける）

```php
// 危険：直接変数を埋め込まない
$posts = DB::select("SELECT * FROM posts WHERE status = '$status'");
```

### 検索機能の実装

```php
// LIKEクエリも安全に
$posts = Post::where('title', 'like', '%' . $search . '%')->get();
```

---

## 認証・認可

### ミドルウェア設定

```php
// routes/web.php
Route::middleware(['auth', 'verified'])->group(function () {
    Route::prefix('admin')->group(function () {
        // 管理画面ルート
    });
});

// 権限チェック
Route::middleware(['auth', 'role:admin'])->group(function () {
    Route::resource('users', UserController::class);
});
```

### ポリシーの実装

```php
// app/Policies/PostPolicy.php
class PostPolicy
{
    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id
            || $user->hasRole(['admin', 'editor']);
    }

    public function delete(User $user, Post $post): bool
    {
        return $user->hasRole('admin');
    }
}
```

### コントローラーでの認可

```php
public function update(Request $request, Post $post)
{
    $this->authorize('update', $post);
    // 更新処理
}
```

### Bladeでの権限チェック

```blade
@can('update', $post)
    <a href="{{ route('posts.edit', $post) }}">編集</a>
@endcan

@role('admin')
    <a href="{{ route('admin.settings') }}">設定</a>
@endrole
```

---

## ファイルアップロード

### バリデーション

```php
// app/Http/Requests/MediaUploadRequest.php
class MediaUploadRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'file' => [
                'required',
                'file',
                'max:10240', // 10MB
                'mimes:jpg,jpeg,png,gif,webp,pdf,doc,docx',
            ],
        ];
    }
}
```

### 安全なファイル保存

```php
public function store(MediaUploadRequest $request)
{
    $file = $request->file('file');

    // ファイル名をランダム化
    $filename = Str::uuid() . '.' . $file->getClientOriginalExtension();

    // publicではなくstorageに保存
    $path = $file->storeAs('media', $filename, 'private');

    // MIMEタイプを再検証
    $mimeType = mime_content_type(storage_path('app/private/' . $path));
    $allowedMimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'];

    if (!in_array($mimeType, $allowedMimes)) {
        Storage::disk('private')->delete($path);
        abort(422, '不正なファイル形式です');
    }

    return Media::create([
        'user_id' => auth()->id(),
        'filename' => $filename,
        'original_name' => $file->getClientOriginalName(),
        'path' => $path,
        'mime_type' => $mimeType,
        'size' => $file->getSize(),
    ]);
}
```

### 画像のリサイズ・最適化

```php
use Intervention\Image\Laravel\Facades\Image;

public function storeImage(Request $request)
{
    $file = $request->file('image');
    $filename = Str::uuid() . '.webp';

    // リサイズして保存
    $image = Image::read($file);
    $image->scale(width: 1200)
          ->toWebp(quality: 80)
          ->save(storage_path('app/public/media/' . $filename));

    // サムネイル作成
    $thumbFilename = 'thumb_' . $filename;
    $image->scale(width: 300)
          ->toWebp(quality: 70)
          ->save(storage_path('app/public/media/' . $thumbFilename));
}
```

---

## セキュリティヘッダー

### ミドルウェア作成

```php
// app/Http/Middleware/SecurityHeaders.php
class SecurityHeaders
{
    public function handle(Request $request, Closure $next): Response
    {
        $response = $next($request);

        $response->headers->set('X-Content-Type-Options', 'nosniff');
        $response->headers->set('X-Frame-Options', 'SAMEORIGIN');
        $response->headers->set('X-XSS-Protection', '1; mode=block');
        $response->headers->set('Referrer-Policy', 'strict-origin-when-cross-origin');
        $response->headers->set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');

        // 本番環境のみ
        if (app()->environment('production')) {
            $response->headers->set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
        }

        return $response;
    }
}
```

### ミドルウェア登録

```php
// bootstrap/app.php
->withMiddleware(function (Middleware $middleware) {
    $middleware->web(append: [
        \App\Http\Middleware\SecurityHeaders::class,
    ]);
})
```

---

## 監査ログ

### Spatie Activity Log設定

```php
// app/Models/Post.php
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class Post extends Model
{
    use LogsActivity;

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['title', 'content', 'status'])
            ->logOnlyDirty()
            ->dontSubmitEmptyLogs()
            ->setDescriptionForEvent(fn(string $eventName) => "記事が{$eventName}されました");
    }
}
```

### ログの確認

```php
// 特定モデルのログ取得
$activities = Activity::forSubject($post)->get();

// ユーザーの操作履歴
$activities = Activity::causedBy($user)->get();
```

### 管理画面でのログ表示

```php
// app/Http/Controllers/Admin/ActivityLogController.php
public function index()
{
    $activities = Activity::with(['causer', 'subject'])
        ->latest()
        ->paginate(50);

    return view('admin.activity-logs.index', compact('activities'));
}
```

---

## その他のセキュリティ対策

### Mass Assignment対策

```php
// app/Models/User.php
class User extends Authenticatable
{
    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    // または明示的にガード
    protected $guarded = ['id', 'is_admin'];
}
```

### レート制限

```php
// routes/api.php
Route::middleware('throttle:60,1')->group(function () {
    Route::post('/login', [AuthController::class, 'login']);
});

// カスタムレート制限
RateLimiter::for('uploads', function (Request $request) {
    return Limit::perMinute(10)->by($request->user()?->id ?: $request->ip());
});
```

### 環境変数の保護

```php
// .env は絶対にGitにコミットしない
// .gitignore に .env を含める

// 本番環境ではconfig:cacheを使用
php artisan config:cache
```

### デバッグモードの無効化

```env
# .env（本番環境）
APP_DEBUG=false
APP_ENV=production
```

### セッションセキュリティ

```php
// config/session.php
'secure' => env('SESSION_SECURE_COOKIE', true),  // HTTPS必須
'http_only' => true,                              // JavaScript からアクセス不可
'same_site' => 'lax',                            // CSRF対策
```

### パスワードポリシー

```php
// app/Http/Requests/RegisterRequest.php
'password' => [
    'required',
    'confirmed',
    Password::min(8)
        ->letters()
        ->mixedCase()
        ->numbers()
        ->symbols()
        ->uncompromised(), // 漏洩パスワードチェック
],
```
