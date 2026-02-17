# データベース設計

## 目次
1. [ER図](#er図)
2. [マイグレーション](#マイグレーション)
3. [モデル](#モデル)
4. [シーダー](#シーダー)

---

## ER図

```
users
├── id
├── name
├── email
├── password
├── avatar
├── created_at
└── updated_at

posts
├── id
├── user_id (FK → users)
├── category_id (FK → categories)
├── title
├── slug (unique)
├── content
├── excerpt
├── featured_image
├── status (draft/published/scheduled)
├── published_at
├── created_at
└── updated_at

categories
├── id
├── parent_id (FK → categories, nullable)
├── name
├── slug (unique)
├── description
├── created_at
└── updated_at

tags
├── id
├── name
├── slug (unique)
├── created_at
└── updated_at

post_tag (pivot)
├── post_id (FK → posts)
└── tag_id (FK → tags)

pages
├── id
├── user_id (FK → users)
├── parent_id (FK → pages, nullable)
├── title
├── slug (unique)
├── content
├── template
├── status (draft/published)
├── sort_order
├── created_at
└── updated_at

media
├── id
├── user_id (FK → users)
├── filename
├── original_name
├── path
├── mime_type
├── size
├── alt_text
├── created_at
└── updated_at
```

---

## マイグレーション

### users テーブル（Laravel標準を拡張）

```php
// database/migrations/xxxx_add_avatar_to_users_table.php
public function up(): void
{
    Schema::table('users', function (Blueprint $table) {
        $table->string('avatar')->nullable()->after('email');
    });
}
```

### categories テーブル

```php
// database/migrations/xxxx_create_categories_table.php
public function up(): void
{
    Schema::create('categories', function (Blueprint $table) {
        $table->id();
        $table->foreignId('parent_id')->nullable()->constrained('categories')->nullOnDelete();
        $table->string('name');
        $table->string('slug')->unique();
        $table->text('description')->nullable();
        $table->timestamps();

        $table->index('parent_id');
    });
}
```

### tags テーブル

```php
// database/migrations/xxxx_create_tags_table.php
public function up(): void
{
    Schema::create('tags', function (Blueprint $table) {
        $table->id();
        $table->string('name');
        $table->string('slug')->unique();
        $table->timestamps();
    });
}
```

### posts テーブル

```php
// database/migrations/xxxx_create_posts_table.php
public function up(): void
{
    Schema::create('posts', function (Blueprint $table) {
        $table->id();
        $table->foreignId('user_id')->constrained()->cascadeOnDelete();
        $table->foreignId('category_id')->nullable()->constrained()->nullOnDelete();
        $table->string('title');
        $table->string('slug')->unique();
        $table->longText('content');
        $table->text('excerpt')->nullable();
        $table->string('featured_image')->nullable();
        $table->enum('status', ['draft', 'published', 'scheduled'])->default('draft');
        $table->timestamp('published_at')->nullable();
        $table->timestamps();

        $table->index(['status', 'published_at']);
        $table->index('user_id');
    });
}
```

### post_tag ピボットテーブル

```php
// database/migrations/xxxx_create_post_tag_table.php
public function up(): void
{
    Schema::create('post_tag', function (Blueprint $table) {
        $table->foreignId('post_id')->constrained()->cascadeOnDelete();
        $table->foreignId('tag_id')->constrained()->cascadeOnDelete();
        $table->primary(['post_id', 'tag_id']);
    });
}
```

### pages テーブル

```php
// database/migrations/xxxx_create_pages_table.php
public function up(): void
{
    Schema::create('pages', function (Blueprint $table) {
        $table->id();
        $table->foreignId('user_id')->constrained()->cascadeOnDelete();
        $table->foreignId('parent_id')->nullable()->constrained('pages')->nullOnDelete();
        $table->string('title');
        $table->string('slug')->unique();
        $table->longText('content');
        $table->string('template')->default('default');
        $table->enum('status', ['draft', 'published'])->default('draft');
        $table->integer('sort_order')->default(0);
        $table->timestamps();

        $table->index(['status', 'sort_order']);
    });
}
```

### media テーブル

```php
// database/migrations/xxxx_create_media_table.php
public function up(): void
{
    Schema::create('media', function (Blueprint $table) {
        $table->id();
        $table->foreignId('user_id')->constrained()->cascadeOnDelete();
        $table->string('filename');
        $table->string('original_name');
        $table->string('path');
        $table->string('mime_type');
        $table->unsignedBigInteger('size');
        $table->string('alt_text')->nullable();
        $table->timestamps();

        $table->index('user_id');
        $table->index('mime_type');
    });
}
```

---

## モデル

### Category モデル

```php
// app/Models/Category.php
class Category extends Model
{
    use HasFactory;

    protected $fillable = [
        'parent_id',
        'name',
        'slug',
        'description',
    ];

    public function parent(): BelongsTo
    {
        return $this->belongsTo(Category::class, 'parent_id');
    }

    public function children(): HasMany
    {
        return $this->hasMany(Category::class, 'parent_id');
    }

    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }

    // スラッグ自動生成
    protected static function booted(): void
    {
        static::creating(function ($category) {
            if (empty($category->slug)) {
                $category->slug = Str::slug($category->name);
            }
        });
    }
}
```

### Tag モデル

```php
// app/Models/Tag.php
class Tag extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'slug'];

    public function posts(): BelongsToMany
    {
        return $this->belongsToMany(Post::class);
    }

    protected static function booted(): void
    {
        static::creating(function ($tag) {
            if (empty($tag->slug)) {
                $tag->slug = Str::slug($tag->name);
            }
        });
    }
}
```

### Post モデル

```php
// app/Models/Post.php
class Post extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'user_id',
        'category_id',
        'title',
        'slug',
        'content',
        'excerpt',
        'featured_image',
        'status',
        'published_at',
    ];

    protected $casts = [
        'published_at' => 'datetime',
    ];

    // リレーション
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class);
    }

    // スコープ
    public function scopePublished(Builder $query): Builder
    {
        return $query->where('status', 'published')
                     ->where('published_at', '<=', now());
    }

    public function scopeDraft(Builder $query): Builder
    {
        return $query->where('status', 'draft');
    }

    // スラッグ自動生成
    protected static function booted(): void
    {
        static::creating(function ($post) {
            if (empty($post->slug)) {
                $post->slug = Str::slug($post->title);
            }
        });
    }

    // 監査ログ設定
    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['title', 'content', 'status'])
            ->logOnlyDirty();
    }
}
```

### Page モデル

```php
// app/Models/Page.php
class Page extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'user_id',
        'parent_id',
        'title',
        'slug',
        'content',
        'template',
        'status',
        'sort_order',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function parent(): BelongsTo
    {
        return $this->belongsTo(Page::class, 'parent_id');
    }

    public function children(): HasMany
    {
        return $this->hasMany(Page::class, 'parent_id')->orderBy('sort_order');
    }

    public function scopePublished(Builder $query): Builder
    {
        return $query->where('status', 'published');
    }

    public function scopeRoot(Builder $query): Builder
    {
        return $query->whereNull('parent_id');
    }

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['title', 'content', 'status'])
            ->logOnlyDirty();
    }
}
```

### Media モデル

```php
// app/Models/Media.php
class Media extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'filename',
        'original_name',
        'path',
        'mime_type',
        'size',
        'alt_text',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function getUrlAttribute(): string
    {
        return Storage::url($this->path);
    }

    public function isImage(): bool
    {
        return str_starts_with($this->mime_type, 'image/');
    }

    public function getHumanSizeAttribute(): string
    {
        $bytes = $this->size;
        $units = ['B', 'KB', 'MB', 'GB'];

        for ($i = 0; $bytes > 1024 && $i < count($units) - 1; $i++) {
            $bytes /= 1024;
        }

        return round($bytes, 2) . ' ' . $units[$i];
    }
}
```

---

## シーダー

### RolePermissionSeeder

```php
// database/seeders/RolePermissionSeeder.php
class RolePermissionSeeder extends Seeder
{
    public function run(): void
    {
        // 権限作成
        $permissions = [
            // 記事
            'posts.view', 'posts.create', 'posts.edit', 'posts.delete', 'posts.publish',
            // ページ
            'pages.view', 'pages.create', 'pages.edit', 'pages.delete', 'pages.publish',
            // メディア
            'media.view', 'media.upload', 'media.delete',
            // ユーザー
            'users.view', 'users.create', 'users.edit', 'users.delete',
            // 設定
            'settings.view', 'settings.edit',
        ];

        foreach ($permissions as $permission) {
            Permission::create(['name' => $permission]);
        }

        // ロール作成
        $superAdmin = Role::create(['name' => 'super-admin']);
        $admin = Role::create(['name' => 'admin']);
        $editor = Role::create(['name' => 'editor']);
        $author = Role::create(['name' => 'author']);

        // 権限割り当て
        $superAdmin->givePermissionTo(Permission::all());

        $admin->givePermissionTo([
            'posts.view', 'posts.create', 'posts.edit', 'posts.delete', 'posts.publish',
            'pages.view', 'pages.create', 'pages.edit', 'pages.delete', 'pages.publish',
            'media.view', 'media.upload', 'media.delete',
            'users.view',
        ]);

        $editor->givePermissionTo([
            'posts.view', 'posts.create', 'posts.edit', 'posts.publish',
            'pages.view', 'pages.create', 'pages.edit', 'pages.publish',
            'media.view', 'media.upload',
        ]);

        $author->givePermissionTo([
            'posts.view', 'posts.create', 'posts.edit',
            'media.view', 'media.upload',
        ]);
    }
}
```

### AdminUserSeeder

```php
// database/seeders/AdminUserSeeder.php
class AdminUserSeeder extends Seeder
{
    public function run(): void
    {
        $admin = User::create([
            'name' => 'Administrator',
            'email' => 'admin@example.com',
            'password' => Hash::make('password'),
            'email_verified_at' => now(),
        ]);

        $admin->assignRole('super-admin');
    }
}
```

### DatabaseSeeder

```php
// database/seeders/DatabaseSeeder.php
class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $this->call([
            RolePermissionSeeder::class,
            AdminUserSeeder::class,
        ]);
    }
}
```
