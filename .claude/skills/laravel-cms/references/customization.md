# カスタマイズガイド

## 目次
1. [コメント機能](#コメント機能)
2. [お問い合わせフォーム](#お問い合わせフォーム)
3. [SEO設定](#seo設定)
4. [サイトマップ](#サイトマップ)
5. [検索機能](#検索機能)
6. [多言語対応](#多言語対応)

---

## コメント機能

### マイグレーション

```php
// database/migrations/xxxx_create_comments_table.php
public function up(): void
{
    Schema::create('comments', function (Blueprint $table) {
        $table->id();
        $table->foreignId('post_id')->constrained()->cascadeOnDelete();
        $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
        $table->foreignId('parent_id')->nullable()->constrained('comments')->cascadeOnDelete();
        $table->string('author_name')->nullable();
        $table->string('author_email')->nullable();
        $table->text('content');
        $table->enum('status', ['pending', 'approved', 'spam'])->default('pending');
        $table->timestamps();

        $table->index(['post_id', 'status']);
    });
}
```

### モデル

```php
// app/Models/Comment.php
class Comment extends Model
{
    use HasFactory;

    protected $fillable = [
        'post_id',
        'user_id',
        'parent_id',
        'author_name',
        'author_email',
        'content',
        'status',
    ];

    public function post(): BelongsTo
    {
        return $this->belongsTo(Post::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function parent(): BelongsTo
    {
        return $this->belongsTo(Comment::class, 'parent_id');
    }

    public function replies(): HasMany
    {
        return $this->hasMany(Comment::class, 'parent_id');
    }

    public function scopeApproved(Builder $query): Builder
    {
        return $query->where('status', 'approved');
    }

    public function getAuthorAttribute(): string
    {
        return $this->user?->name ?? $this->author_name ?? 'Anonymous';
    }
}
```

### コントローラー

```php
// app/Http/Controllers/CommentController.php
class CommentController extends Controller
{
    public function store(StoreCommentRequest $request, Post $post)
    {
        $comment = $post->comments()->create([
            'user_id' => auth()->id(),
            'parent_id' => $request->parent_id,
            'author_name' => auth()->check() ? null : $request->author_name,
            'author_email' => auth()->check() ? null : $request->author_email,
            'content' => $request->content,
            'status' => auth()->check() ? 'approved' : 'pending',
        ]);

        return back()->with('success', 'コメントを投稿しました');
    }
}

// app/Http/Controllers/Admin/CommentController.php
class CommentController extends Controller
{
    public function index()
    {
        $comments = Comment::with(['post', 'user'])
            ->when(request('status'), fn($q, $status) => $q->where('status', $status))
            ->latest()
            ->paginate(20);

        return view('admin.comments.index', compact('comments'));
    }

    public function approve(Comment $comment)
    {
        $comment->update(['status' => 'approved']);
        return back()->with('success', 'コメントを承認しました');
    }

    public function spam(Comment $comment)
    {
        $comment->update(['status' => 'spam']);
        return back()->with('success', 'スパムとしてマークしました');
    }

    public function destroy(Comment $comment)
    {
        $comment->delete();
        return back()->with('success', 'コメントを削除しました');
    }
}
```

---

## お問い合わせフォーム

### マイグレーション

```php
// database/migrations/xxxx_create_contacts_table.php
public function up(): void
{
    Schema::create('contacts', function (Blueprint $table) {
        $table->id();
        $table->string('name');
        $table->string('email');
        $table->string('subject')->nullable();
        $table->text('message');
        $table->enum('status', ['unread', 'read', 'replied'])->default('unread');
        $table->timestamp('read_at')->nullable();
        $table->timestamps();
    });
}
```

### コントローラー

```php
// app/Http/Controllers/ContactController.php
class ContactController extends Controller
{
    public function create()
    {
        return view('contact');
    }

    public function store(StoreContactRequest $request)
    {
        $contact = Contact::create($request->validated());

        // 管理者に通知
        Mail::to(config('mail.admin_address'))->send(new ContactReceived($contact));

        return redirect()
            ->route('contact.thanks')
            ->with('success', 'お問い合わせを受け付けました');
    }
}
```

### フォームリクエスト（スパム対策）

```php
// app/Http/Requests/StoreContactRequest.php
class StoreContactRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'name' => ['required', 'string', 'max:100'],
            'email' => ['required', 'email', 'max:255'],
            'subject' => ['nullable', 'string', 'max:200'],
            'message' => ['required', 'string', 'max:5000'],
            'honeypot' => ['present', 'max:0'], // スパム対策
        ];
    }
}
```

### Bladeテンプレート

```blade
{{-- resources/views/contact.blade.php --}}
<form method="POST" action="{{ route('contact.store') }}">
    @csrf

    {{-- ハニーポット（スパム対策） --}}
    <div style="display: none;">
        <input type="text" name="honeypot" value="">
    </div>

    <div>
        <label for="name">お名前</label>
        <input type="text" name="name" id="name" value="{{ old('name') }}" required>
        @error('name') <span>{{ $message }}</span> @enderror
    </div>

    <div>
        <label for="email">メールアドレス</label>
        <input type="email" name="email" id="email" value="{{ old('email') }}" required>
        @error('email') <span>{{ $message }}</span> @enderror
    </div>

    <div>
        <label for="subject">件名</label>
        <input type="text" name="subject" id="subject" value="{{ old('subject') }}">
    </div>

    <div>
        <label for="message">メッセージ</label>
        <textarea name="message" id="message" rows="5" required>{{ old('message') }}</textarea>
        @error('message') <span>{{ $message }}</span> @enderror
    </div>

    <button type="submit">送信</button>
</form>
```

---

## SEO設定

### マイグレーション

```php
// database/migrations/xxxx_create_seo_metas_table.php
public function up(): void
{
    Schema::create('seo_metas', function (Blueprint $table) {
        $table->id();
        $table->morphs('seoable');
        $table->string('meta_title')->nullable();
        $table->text('meta_description')->nullable();
        $table->string('meta_keywords')->nullable();
        $table->string('og_image')->nullable();
        $table->string('canonical_url')->nullable();
        $table->boolean('noindex')->default(false);
        $table->timestamps();
    });
}
```

### トレイト

```php
// app/Traits/HasSeoMeta.php
trait HasSeoMeta
{
    public function seoMeta(): MorphOne
    {
        return $this->morphOne(SeoMeta::class, 'seoable');
    }

    public function getMetaTitleAttribute(): string
    {
        return $this->seoMeta?->meta_title ?? $this->title;
    }

    public function getMetaDescriptionAttribute(): ?string
    {
        return $this->seoMeta?->meta_description ?? Str::limit(strip_tags($this->content), 160);
    }
}
```

### Bladeコンポーネント

```php
// app/View/Components/SeoHead.php
class SeoHead extends Component
{
    public function __construct(
        public ?string $title = null,
        public ?string $description = null,
        public ?string $image = null,
        public ?string $canonical = null,
        public bool $noindex = false,
    ) {}

    public function render()
    {
        return view('components.seo-head');
    }
}
```

```blade
{{-- resources/views/components/seo-head.blade.php --}}
<title>{{ $title ?? config('app.name') }}</title>
<meta name="description" content="{{ $description ?? '' }}">

@if($noindex)
<meta name="robots" content="noindex, nofollow">
@endif

@if($canonical)
<link rel="canonical" href="{{ $canonical }}">
@endif

{{-- Open Graph --}}
<meta property="og:title" content="{{ $title ?? config('app.name') }}">
<meta property="og:description" content="{{ $description ?? '' }}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{ url()->current() }}">
@if($image)
<meta property="og:image" content="{{ $image }}">
@endif

{{-- Twitter Card --}}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ $title ?? config('app.name') }}">
<meta name="twitter:description" content="{{ $description ?? '' }}">
@if($image)
<meta name="twitter:image" content="{{ $image }}">
@endif
```

### 使用例

```blade
<head>
    <x-seo-head
        :title="$post->meta_title . ' | ' . config('app.name')"
        :description="$post->meta_description"
        :image="$post->featured_image"
        :canonical="route('posts.show', $post)"
    />
</head>
```

---

## サイトマップ

### コントローラー

```php
// app/Http/Controllers/SitemapController.php
class SitemapController extends Controller
{
    public function index()
    {
        $posts = Post::published()->latest('published_at')->get();
        $pages = Page::published()->get();

        return response()
            ->view('sitemap', compact('posts', 'pages'))
            ->header('Content-Type', 'application/xml');
    }
}
```

### Bladeテンプレート

```blade
{{-- resources/views/sitemap.blade.php --}}
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{{ url('/') }}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>

    @foreach($posts as $post)
    <url>
        <loc>{{ route('posts.show', $post) }}</loc>
        <lastmod>{{ $post->updated_at->toAtomString() }}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    @endforeach

    @foreach($pages as $page)
    <url>
        <loc>{{ route('pages.show', $page) }}</loc>
        <lastmod>{{ $page->updated_at->toAtomString() }}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    @endforeach
</urlset>
```

### ルート

```php
Route::get('/sitemap.xml', [SitemapController::class, 'index'])->name('sitemap');
```

---

## 検索機能

### 基本的な検索

```php
// app/Http/Controllers/SearchController.php
class SearchController extends Controller
{
    public function index(Request $request)
    {
        $query = $request->input('q');

        if (empty($query)) {
            return view('search', ['results' => collect(), 'query' => '']);
        }

        $posts = Post::published()
            ->where(function ($q) use ($query) {
                $q->where('title', 'like', "%{$query}%")
                  ->orWhere('content', 'like', "%{$query}%");
            })
            ->latest('published_at')
            ->paginate(10)
            ->withQueryString();

        return view('search', [
            'results' => $posts,
            'query' => $query,
        ]);
    }
}
```

### 全文検索（MySQL）

```php
// マイグレーションでFULLTEXTインデックス追加
Schema::table('posts', function (Blueprint $table) {
    $table->fullText(['title', 'content']);
});

// 検索クエリ
$posts = Post::published()
    ->whereFullText(['title', 'content'], $query)
    ->paginate(10);
```

---

## 多言語対応

### 設定

```php
// config/app.php
'locale' => 'ja',
'fallback_locale' => 'ja',
'available_locales' => ['ja', 'en'],
```

### ミドルウェア

```php
// app/Http/Middleware/SetLocale.php
class SetLocale
{
    public function handle(Request $request, Closure $next): Response
    {
        $locale = $request->segment(1);

        if (in_array($locale, config('app.available_locales'))) {
            app()->setLocale($locale);
        }

        return $next($request);
    }
}
```

### ルート

```php
Route::prefix('{locale}')
    ->where(['locale' => implode('|', config('app.available_locales'))])
    ->middleware('set-locale')
    ->group(function () {
        Route::get('/', [HomeController::class, 'index'])->name('home');
        Route::get('/posts/{post:slug}', [PostController::class, 'show'])->name('posts.show');
    });
```

### 言語切り替えコンポーネント

```blade
{{-- resources/views/components/language-switcher.blade.php --}}
<div class="language-switcher">
    @foreach(config('app.available_locales') as $locale)
        <a href="{{ route(Route::currentRouteName(), array_merge(Route::current()->parameters(), ['locale' => $locale])) }}"
           class="{{ app()->getLocale() === $locale ? 'active' : '' }}">
            {{ strtoupper($locale) }}
        </a>
    @endforeach
</div>
```

### 翻訳ファイル

```php
// lang/ja/messages.php
return [
    'welcome' => 'ようこそ',
    'read_more' => '続きを読む',
    'posted_at' => ':date に投稿',
];

// lang/en/messages.php
return [
    'welcome' => 'Welcome',
    'read_more' => 'Read more',
    'posted_at' => 'Posted on :date',
];
```

### 使用例

```blade
<h1>{{ __('messages.welcome') }}</h1>
<a href="#">{{ __('messages.read_more') }}</a>
<p>{{ __('messages.posted_at', ['date' => $post->published_at->format('Y-m-d')]) }}</p>
```
