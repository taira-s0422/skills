# 機能実装ガイド

## 目次
1. [記事管理](#記事管理)
2. [ページ管理](#ページ管理)
3. [メディア管理](#メディア管理)
4. [ユーザー・権限管理](#ユーザー権限管理)

---

## 記事管理

### コントローラー

```php
// app/Http/Controllers/Admin/PostController.php
class PostController extends Controller
{
    public function __construct()
    {
        $this->authorizeResource(Post::class, 'post');
    }

    public function index()
    {
        $posts = Post::with(['user', 'category'])
            ->when(request('status'), fn($q, $status) => $q->where('status', $status))
            ->when(request('search'), fn($q, $search) =>
                $q->where('title', 'like', "%{$search}%")
            )
            ->latest()
            ->paginate(20);

        return view('admin.posts.index', compact('posts'));
    }

    public function create()
    {
        $categories = Category::all();
        $tags = Tag::all();

        return view('admin.posts.create', compact('categories', 'tags'));
    }

    public function store(StorePostRequest $request)
    {
        $post = Post::create([
            'user_id' => auth()->id(),
            ...$request->validated(),
        ]);

        if ($request->has('tags')) {
            $post->tags()->sync($request->tags);
        }

        return redirect()
            ->route('admin.posts.index')
            ->with('success', '記事を作成しました');
    }

    public function edit(Post $post)
    {
        $categories = Category::all();
        $tags = Tag::all();

        return view('admin.posts.edit', compact('post', 'categories', 'tags'));
    }

    public function update(UpdatePostRequest $request, Post $post)
    {
        $post->update($request->validated());

        if ($request->has('tags')) {
            $post->tags()->sync($request->tags);
        }

        return redirect()
            ->route('admin.posts.index')
            ->with('success', '記事を更新しました');
    }

    public function destroy(Post $post)
    {
        $post->delete();

        return redirect()
            ->route('admin.posts.index')
            ->with('success', '記事を削除しました');
    }
}
```

### フォームリクエスト

```php
// app/Http/Requests/StorePostRequest.php
class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('posts.create');
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'slug' => ['nullable', 'string', 'max:255', 'unique:posts,slug'],
            'content' => ['required', 'string'],
            'excerpt' => ['nullable', 'string', 'max:500'],
            'category_id' => ['nullable', 'exists:categories,id'],
            'featured_image' => ['nullable', 'string'],
            'status' => ['required', 'in:draft,published,scheduled'],
            'published_at' => ['nullable', 'date', 'required_if:status,scheduled'],
            'tags' => ['nullable', 'array'],
            'tags.*' => ['exists:tags,id'],
        ];
    }
}
```

### ポリシー

```php
// app/Policies/PostPolicy.php
class PostPolicy
{
    public function viewAny(User $user): bool
    {
        return $user->can('posts.view');
    }

    public function view(User $user, Post $post): bool
    {
        return $user->can('posts.view');
    }

    public function create(User $user): bool
    {
        return $user->can('posts.create');
    }

    public function update(User $user, Post $post): bool
    {
        if ($user->can('posts.edit')) {
            return true;
        }

        // authorは自分の記事のみ編集可能
        return $user->hasRole('author') && $post->user_id === $user->id;
    }

    public function delete(User $user, Post $post): bool
    {
        return $user->can('posts.delete');
    }
}
```

### ルート

```php
// routes/web.php
Route::middleware(['auth', 'verified'])->prefix('admin')->name('admin.')->group(function () {
    Route::resource('posts', PostController::class);
    Route::resource('pages', PageController::class);
    Route::resource('media', MediaController::class)->only(['index', 'store', 'destroy']);
    Route::resource('categories', CategoryController::class);
    Route::resource('tags', TagController::class);
    Route::resource('users', UserController::class);
});
```

---

## ページ管理

### コントローラー

```php
// app/Http/Controllers/Admin/PageController.php
class PageController extends Controller
{
    public function __construct()
    {
        $this->authorizeResource(Page::class, 'page');
    }

    public function index()
    {
        $pages = Page::with('parent')
            ->root()
            ->with('children')
            ->orderBy('sort_order')
            ->get();

        return view('admin.pages.index', compact('pages'));
    }

    public function create()
    {
        $pages = Page::published()->get();
        $templates = $this->getTemplates();

        return view('admin.pages.create', compact('pages', 'templates'));
    }

    public function store(StorePageRequest $request)
    {
        Page::create([
            'user_id' => auth()->id(),
            ...$request->validated(),
        ]);

        return redirect()
            ->route('admin.pages.index')
            ->with('success', 'ページを作成しました');
    }

    public function edit(Page $page)
    {
        $pages = Page::published()
            ->where('id', '!=', $page->id)
            ->get();
        $templates = $this->getTemplates();

        return view('admin.pages.edit', compact('page', 'pages', 'templates'));
    }

    public function update(UpdatePageRequest $request, Page $page)
    {
        $page->update($request->validated());

        return redirect()
            ->route('admin.pages.index')
            ->with('success', 'ページを更新しました');
    }

    public function destroy(Page $page)
    {
        // 子ページがある場合は親を解除
        $page->children()->update(['parent_id' => null]);
        $page->delete();

        return redirect()
            ->route('admin.pages.index')
            ->with('success', 'ページを削除しました');
    }

    private function getTemplates(): array
    {
        return [
            'default' => 'デフォルト',
            'full-width' => '全幅',
            'sidebar' => 'サイドバー付き',
            'landing' => 'ランディングページ',
        ];
    }
}
```

### 並び替え（Ajax）

```php
// app/Http/Controllers/Admin/PageOrderController.php
class PageOrderController extends Controller
{
    public function update(Request $request)
    {
        $request->validate([
            'pages' => ['required', 'array'],
            'pages.*.id' => ['required', 'exists:pages,id'],
            'pages.*.sort_order' => ['required', 'integer'],
        ]);

        foreach ($request->pages as $item) {
            Page::where('id', $item['id'])->update(['sort_order' => $item['sort_order']]);
        }

        return response()->json(['message' => '並び順を更新しました']);
    }
}
```

---

## メディア管理

### コントローラー

```php
// app/Http/Controllers/Admin/MediaController.php
class MediaController extends Controller
{
    public function index()
    {
        $media = Media::with('user')
            ->when(request('type'), function ($query, $type) {
                return match($type) {
                    'image' => $query->where('mime_type', 'like', 'image/%'),
                    'document' => $query->whereIn('mime_type', [
                        'application/pdf',
                        'application/msword',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    ]),
                    default => $query,
                };
            })
            ->latest()
            ->paginate(24);

        return view('admin.media.index', compact('media'));
    }

    public function store(MediaUploadRequest $request)
    {
        $file = $request->file('file');
        $filename = Str::uuid() . '.' . $file->getClientOriginalExtension();

        // 画像の場合は最適化
        if (str_starts_with($file->getMimeType(), 'image/')) {
            $path = $this->processImage($file, $filename);
        } else {
            $path = $file->storeAs('media', $filename, 'public');
        }

        $media = Media::create([
            'user_id' => auth()->id(),
            'filename' => $filename,
            'original_name' => $file->getClientOriginalName(),
            'path' => $path,
            'mime_type' => $file->getMimeType(),
            'size' => $file->getSize(),
        ]);

        if ($request->wantsJson()) {
            return response()->json([
                'id' => $media->id,
                'url' => $media->url,
                'name' => $media->original_name,
            ]);
        }

        return redirect()
            ->route('admin.media.index')
            ->with('success', 'ファイルをアップロードしました');
    }

    public function destroy(Media $media)
    {
        $this->authorize('media.delete');

        Storage::disk('public')->delete($media->path);
        $media->delete();

        return redirect()
            ->route('admin.media.index')
            ->with('success', 'ファイルを削除しました');
    }

    private function processImage($file, $filename): string
    {
        $image = Image::read($file);

        // 大きすぎる場合はリサイズ
        if ($image->width() > 1920) {
            $image->scale(width: 1920);
        }

        $path = 'media/' . $filename;
        $image->save(storage_path('app/public/' . $path));

        return $path;
    }
}
```

### メディア選択モーダル（JavaScript）

```javascript
// resources/js/media-picker.js
class MediaPicker {
    constructor(options = {}) {
        this.onSelect = options.onSelect || (() => {});
        this.modal = null;
    }

    open() {
        this.modal = document.createElement('div');
        this.modal.className = 'media-picker-modal';
        this.modal.innerHTML = `
            <div class="media-picker-content">
                <div class="media-picker-header">
                    <h3>メディアを選択</h3>
                    <button type="button" class="close-btn">&times;</button>
                </div>
                <div class="media-picker-body">
                    <div class="media-upload">
                        <input type="file" id="media-upload-input" accept="image/*">
                        <label for="media-upload-input">ファイルをアップロード</label>
                    </div>
                    <div class="media-grid" id="media-grid"></div>
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);
        this.loadMedia();
        this.bindEvents();
    }

    async loadMedia() {
        const response = await fetch('/admin/media?type=image', {
            headers: { 'Accept': 'application/json' }
        });
        const data = await response.json();

        const grid = document.getElementById('media-grid');
        grid.innerHTML = data.data.map(item => `
            <div class="media-item" data-id="${item.id}" data-url="${item.url}">
                <img src="${item.url}" alt="${item.original_name}">
            </div>
        `).join('');
    }

    bindEvents() {
        this.modal.querySelector('.close-btn').addEventListener('click', () => this.close());
        this.modal.querySelector('.media-grid').addEventListener('click', (e) => {
            const item = e.target.closest('.media-item');
            if (item) {
                this.onSelect({
                    id: item.dataset.id,
                    url: item.dataset.url
                });
                this.close();
            }
        });
    }

    close() {
        this.modal.remove();
    }
}
```

---

## ユーザー・権限管理

### コントローラー

```php
// app/Http/Controllers/Admin/UserController.php
class UserController extends Controller
{
    public function __construct()
    {
        $this->middleware('permission:users.view')->only(['index', 'show']);
        $this->middleware('permission:users.create')->only(['create', 'store']);
        $this->middleware('permission:users.edit')->only(['edit', 'update']);
        $this->middleware('permission:users.delete')->only('destroy');
    }

    public function index()
    {
        $users = User::with('roles')
            ->when(request('role'), fn($q, $role) => $q->role($role))
            ->when(request('search'), fn($q, $search) =>
                $q->where('name', 'like', "%{$search}%")
                  ->orWhere('email', 'like', "%{$search}%")
            )
            ->paginate(20);

        $roles = Role::all();

        return view('admin.users.index', compact('users', 'roles'));
    }

    public function create()
    {
        $roles = Role::all();

        return view('admin.users.create', compact('roles'));
    }

    public function store(StoreUserRequest $request)
    {
        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
        ]);

        $user->assignRole($request->role);

        return redirect()
            ->route('admin.users.index')
            ->with('success', 'ユーザーを作成しました');
    }

    public function edit(User $user)
    {
        $roles = Role::all();

        return view('admin.users.edit', compact('user', 'roles'));
    }

    public function update(UpdateUserRequest $request, User $user)
    {
        $user->update([
            'name' => $request->name,
            'email' => $request->email,
        ]);

        if ($request->filled('password')) {
            $user->update(['password' => Hash::make($request->password)]);
        }

        $user->syncRoles([$request->role]);

        return redirect()
            ->route('admin.users.index')
            ->with('success', 'ユーザーを更新しました');
    }

    public function destroy(User $user)
    {
        // 自分自身は削除不可
        if ($user->id === auth()->id()) {
            return back()->with('error', '自分自身は削除できません');
        }

        $user->delete();

        return redirect()
            ->route('admin.users.index')
            ->with('success', 'ユーザーを削除しました');
    }
}
```

### ユーザーモデルの設定

```php
// app/Models/User.php
use Spatie\Permission\Traits\HasRoles;
use Spatie\Activitylog\Traits\CausesActivity;

class User extends Authenticatable
{
    use HasFactory, Notifiable, HasRoles, CausesActivity;

    protected $fillable = [
        'name',
        'email',
        'password',
        'avatar',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
        ];
    }

    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }

    public function pages(): HasMany
    {
        return $this->hasMany(Page::class);
    }

    public function media(): HasMany
    {
        return $this->hasMany(Media::class);
    }
}
```
