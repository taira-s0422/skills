# 静的HTML → Blade変換ガイド

## 目次
1. [ワークフロー概要](#ワークフロー概要)
2. [テンプレート配置](#テンプレート配置)
3. [レイアウト抽出](#レイアウト抽出)
4. [Bladeコンポーネント化](#bladeコンポーネント化)
5. [CMS連携](#cms連携)
6. [アセット管理](#アセット管理)
7. [実践例](#実践例)

---

## ワークフロー概要

```
1. 静的HTMLを resources/templates/static/ に配置
      ↓
2. 共通部分を分析（header, footer, sidebar等）
      ↓
3. Bladeレイアウト作成（layouts/app.blade.php）
      ↓
4. 再利用可能な要素をコンポーネント化
      ↓
5. 静的コンテンツをDB/CMS連携に変換
      ↓
6. CSS/JS/画像をpublic/に配置
```

---

## テンプレート配置

### ディレクトリ構成

```
resources/
├── templates/
│   └── static/           # 元の静的HTMLを保存（参照用）
│       ├── index.html
│       ├── about.html
│       ├── blog.html
│       ├── blog-single.html
│       ├── contact.html
│       ├── css/
│       ├── js/
│       └── images/
└── views/
    ├── layouts/
    │   └── app.blade.php
    ├── components/
    │   ├── header.blade.php
    │   ├── footer.blade.php
    │   └── ...
    ├── home.blade.php
    ├── posts/
    │   ├── index.blade.php
    │   └── show.blade.php
    └── pages/
        └── show.blade.php
```

---

## レイアウト抽出

### 静的HTMLの分析

元のHTMLから共通部分を特定：

```html
<!-- 元の静的HTML（例：index.html） -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>サイト名</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <!-- ここから Header（共通） -->
    <header>
        <nav>...</nav>
    </header>
    <!-- ここまで Header -->

    <!-- ここから Main Content（ページごとに異なる） -->
    <main>
        <h1>ページタイトル</h1>
        <p>コンテンツ...</p>
    </main>
    <!-- ここまで Main Content -->

    <!-- ここから Footer（共通） -->
    <footer>
        <p>&copy; 2024 Company</p>
    </footer>
    <!-- ここまで Footer -->

    <script src="js/main.js"></script>
</body>
</html>
```

### Bladeレイアウト作成

```blade
{{-- resources/views/layouts/app.blade.php --}}
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <title>@yield('title', config('app.name'))</title>

    {{-- SEOメタ --}}
    @hasSection('meta_description')
    <meta name="description" content="@yield('meta_description')">
    @endif

    {{-- スタイル --}}
    <link rel="stylesheet" href="{{ asset('css/style.css') }}">
    @stack('styles')
</head>
<body class="@yield('body_class')">
    <x-header />

    <main>
        @yield('content')
    </main>

    <x-footer />

    {{-- スクリプト --}}
    <script src="{{ asset('js/main.js') }}"></script>
    @stack('scripts')
</body>
</html>
```

---

## Bladeコンポーネント化

### Headerコンポーネント

```blade
{{-- resources/views/components/header.blade.php --}}
<header class="site-header">
    <div class="container">
        <a href="{{ route('home') }}" class="logo">
            <img src="{{ asset('images/logo.png') }}" alt="{{ config('app.name') }}">
        </a>

        <nav class="main-nav">
            <ul>
                <li><a href="{{ route('home') }}" @class(['active' => request()->routeIs('home')])>ホーム</a></li>
                <li><a href="{{ route('posts.index') }}" @class(['active' => request()->routeIs('posts.*')])>ブログ</a></li>
                @foreach($pages ?? [] as $page)
                <li><a href="{{ route('pages.show', $page) }}" @class(['active' => request()->is('pages/' . $page->slug)])>{{ $page->title }}</a></li>
                @endforeach
                <li><a href="{{ route('contact') }}" @class(['active' => request()->routeIs('contact')])>お問い合わせ</a></li>
            </ul>
        </nav>

        <button class="mobile-menu-toggle" aria-label="メニュー">
            <span></span>
        </button>
    </div>
</header>
```

### Footerコンポーネント

```blade
{{-- resources/views/components/footer.blade.php --}}
<footer class="site-footer">
    <div class="container">
        <div class="footer-widgets">
            <div class="widget">
                <h4>{{ config('app.name') }}</h4>
                <p>サイトの説明文...</p>
            </div>

            <div class="widget">
                <h4>リンク</h4>
                <ul>
                    @foreach($footerPages ?? [] as $page)
                    <li><a href="{{ route('pages.show', $page) }}">{{ $page->title }}</a></li>
                    @endforeach
                </ul>
            </div>

            <div class="widget">
                <h4>最新記事</h4>
                <ul>
                    @foreach($recentPosts ?? [] as $post)
                    <li><a href="{{ route('posts.show', $post) }}">{{ $post->title }}</a></li>
                    @endforeach
                </ul>
            </div>
        </div>

        <div class="footer-bottom">
            <p>&copy; {{ date('Y') }} {{ config('app.name') }}. All rights reserved.</p>
        </div>
    </div>
</footer>
```

### 汎用コンポーネント

```blade
{{-- resources/views/components/card.blade.php --}}
@props([
    'title' => '',
    'image' => null,
    'link' => '#',
    'date' => null,
])

<article {{ $attributes->merge(['class' => 'card']) }}>
    @if($image)
    <a href="{{ $link }}" class="card-image">
        <img src="{{ $image }}" alt="{{ $title }}">
    </a>
    @endif

    <div class="card-body">
        @if($date)
        <time datetime="{{ $date->toDateString() }}">{{ $date->format('Y.m.d') }}</time>
        @endif

        <h3 class="card-title">
            <a href="{{ $link }}">{{ $title }}</a>
        </h3>

        {{ $slot }}
    </div>
</article>
```

### 使用例

```blade
<x-card
    :title="$post->title"
    :image="$post->featured_image"
    :link="route('posts.show', $post)"
    :date="$post->published_at"
>
    <p>{{ $post->excerpt }}</p>
</x-card>
```

---

## CMS連携

### 静的コンテンツ → 動的コンテンツ

**Before（静的）:**
```html
<h1>会社概要</h1>
<p>私たちは2010年に設立されました...</p>
```

**After（CMS連携）:**
```blade
<h1>{{ $page->title }}</h1>
{!! $page->content !!}
```

### 記事一覧の変換

**Before（静的）:**
```html
<div class="blog-list">
    <article>
        <img src="images/post1.jpg" alt="">
        <h3><a href="blog-single.html">記事タイトル1</a></h3>
        <p>2024年1月1日</p>
    </article>
    <!-- 繰り返し... -->
</div>
```

**After（CMS連携）:**
```blade
<div class="blog-list">
    @forelse($posts as $post)
    <x-card
        :title="$post->title"
        :image="$post->featured_image"
        :link="route('posts.show', $post)"
        :date="$post->published_at"
    >
        <p>{{ Str::limit($post->excerpt, 100) }}</p>
    </x-card>
    @empty
    <p>記事がありません。</p>
    @endforelse
</div>

{{ $posts->links() }}
```

### ナビゲーションの動的化

**Before（静的）:**
```html
<nav>
    <a href="index.html">ホーム</a>
    <a href="about.html">会社概要</a>
    <a href="services.html">サービス</a>
    <a href="contact.html">お問い合わせ</a>
</nav>
```

**After（CMS連携）:**
```blade
<nav>
    <a href="{{ route('home') }}">ホーム</a>
    @foreach($navPages as $page)
    <a href="{{ route('pages.show', $page) }}">{{ $page->title }}</a>
    @endforeach
    <a href="{{ route('contact') }}">お問い合わせ</a>
</nav>
```

---

## アセット管理

### ファイル配置

```
public/
├── css/
│   └── style.css       # 静的HTMLからコピー
├── js/
│   └── main.js         # 静的HTMLからコピー
├── images/
│   ├── logo.png
│   └── ...
└── fonts/
    └── ...
```

### パス変換

**Before:**
```html
<link rel="stylesheet" href="css/style.css">
<img src="images/hero.jpg" alt="">
<script src="js/main.js"></script>
```

**After:**
```blade
<link rel="stylesheet" href="{{ asset('css/style.css') }}">
<img src="{{ asset('images/hero.jpg') }}" alt="">
<script src="{{ asset('js/main.js') }}"></script>
```

### Vite使用時（推奨）

```blade
{{-- resources/views/layouts/app.blade.php --}}
<head>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
```

```javascript
// vite.config.js
export default defineConfig({
    plugins: [laravel(['resources/css/app.css', 'resources/js/app.js'])],
});
```

---

## 実践例

### 完全な変換例：ブログ記事ページ

**元の静的HTML（blog-single.html）:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>記事タイトル - サイト名</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <nav>...</nav>
    </header>

    <main class="blog-single">
        <article>
            <img src="images/featured.jpg" alt="" class="featured-image">
            <h1>記事タイトル</h1>
            <div class="meta">
                <span>2024年1月15日</span>
                <span>カテゴリ名</span>
            </div>
            <div class="content">
                <p>記事の本文...</p>
            </div>
            <div class="tags">
                <a href="#">タグ1</a>
                <a href="#">タグ2</a>
            </div>
        </article>

        <aside class="sidebar">
            <div class="widget">
                <h4>カテゴリ</h4>
                <ul>
                    <li><a href="#">カテゴリ1</a></li>
                    <li><a href="#">カテゴリ2</a></li>
                </ul>
            </div>
        </aside>
    </main>

    <footer>...</footer>
    <script src="js/main.js"></script>
</body>
</html>
```

**Blade変換後（posts/show.blade.php）:**
```blade
@extends('layouts.app')

@section('title', $post->title . ' | ' . config('app.name'))
@section('meta_description', $post->excerpt)
@section('body_class', 'blog-single-page')

@section('content')
<main class="blog-single">
    <article>
        @if($post->featured_image)
        <img src="{{ Storage::url($post->featured_image) }}" alt="{{ $post->title }}" class="featured-image">
        @endif

        <h1>{{ $post->title }}</h1>

        <div class="meta">
            <time datetime="{{ $post->published_at->toDateString() }}">
                {{ $post->published_at->format('Y年n月j日') }}
            </time>
            @if($post->category)
            <a href="{{ route('categories.show', $post->category) }}">{{ $post->category->name }}</a>
            @endif
        </div>

        <div class="content">
            {!! $post->content !!}
        </div>

        @if($post->tags->isNotEmpty())
        <div class="tags">
            @foreach($post->tags as $tag)
            <a href="{{ route('tags.show', $tag) }}">{{ $tag->name }}</a>
            @endforeach
        </div>
        @endif
    </article>

    <aside class="sidebar">
        <x-widget.categories :categories="$categories" />
        <x-widget.recent-posts :posts="$recentPosts" />
    </aside>
</main>
@endsection
```

### チェックリスト

変換時の確認項目：

- [ ] 全ての静的リンクをLaravelルートに変換
- [ ] 画像パスを `asset()` または `Storage::url()` に変換
- [ ] フォームに `@csrf` を追加
- [ ] 動的コンテンツを変数/ループに置換
- [ ] metaタグをSEO対応に
- [ ] アクティブ状態のクラス付与
- [ ] エラーメッセージ表示の追加
- [ ] フラッシュメッセージの表示
- [ ] ページネーションの実装
