# 実装ガイドライン

## 目次
- [HTML構造テンプレート](#html構造テンプレート)
- [リキッドデザイン実装](#リキッドデザイン実装)
- [レスポンシブパターン](#レスポンシブパターン)
- [よく使うCSSパターン](#よく使うcssパターン)
- [トラブルシューティング](#トラブルシューティング)

---

## HTML構造テンプレート

### 基本ページ構造

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="ページの説明文">
  <title>ページタイトル | サイト名</title>

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">

  <!-- OGP -->
  <meta property="og:title" content="ページタイトル">
  <meta property="og:description" content="ページの説明文">
  <meta property="og:image" content="https://example.com/ogp.jpg">
  <meta property="og:url" content="https://example.com/">
  <meta property="og:type" content="website">

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Montserrat:wght@400;700&display=swap" rel="stylesheet">

  <!-- CSS -->
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <!-- Header -->
  <header class="l-header">
    <div class="l-container">
      <div class="l-header__inner">
        <a href="/" class="l-header__logo">Logo</a>
        <nav class="l-header__nav">
          <ul class="c-nav">
            <li class="c-nav__item"><a href="/">TOP</a></li>
            <li class="c-nav__item"><a href="/about.html">About</a></li>
            <li class="c-nav__item"><a href="/service.html">Service</a></li>
            <li class="c-nav__item"><a href="/contact.html">Contact</a></li>
          </ul>
        </nav>
        <button class="c-hamburger u-sp-only" aria-label="メニュー">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="p-top">
    <!-- Hero Section -->
    <section class="p-top__hero">
      <div class="l-container">
        <h1 class="p-top__hero-title">メインタイトル</h1>
        <p class="p-top__hero-subtitle">サブタイトルテキスト</p>
        <a href="/contact.html" class="c-button c-button--primary c-button--large">
          お問い合わせ
        </a>
      </div>
    </section>

    <!-- Feature Section -->
    <section class="p-top__feature">
      <div class="l-container">
        <h2 class="c-heading c-heading--h2 c-heading--center">
          <span class="c-heading__sub">FEATURE</span>
          特徴
        </h2>
        <div class="p-top__feature-list">
          <article class="c-card">
            <div class="c-card__image">
              <img src="images/feature01.jpg" alt="特徴1の画像">
            </div>
            <div class="c-card__body">
              <h3 class="c-card__title">特徴1</h3>
              <p class="c-card__text">説明テキスト</p>
            </div>
          </article>
          <!-- 繰り返し -->
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="p-top__cta">
      <div class="l-container">
        <h2 class="c-heading c-heading--h2 c-heading--center">お問い合わせ</h2>
        <p class="u-text-center u-mb-30">お気軽にご連絡ください</p>
        <div class="u-text-center">
          <a href="/contact.html" class="c-button c-button--primary c-button--large">
            お問い合わせはこちら
          </a>
        </div>
      </div>
    </section>
  </main>

  <!-- Footer -->
  <footer class="l-footer">
    <div class="l-container">
      <div class="l-footer__inner">
        <div class="l-footer__logo">Logo</div>
        <nav class="l-footer__nav">
          <ul>
            <li><a href="/">TOP</a></li>
            <li><a href="/about.html">About</a></li>
            <li><a href="/service.html">Service</a></li>
            <li><a href="/contact.html">Contact</a></li>
          </ul>
        </nav>
      </div>
      <p class="l-footer__copyright">
        &copy; 2024 Company Name. All Rights Reserved.
      </p>
    </div>
  </footer>

  <!-- JavaScript -->
  <script src="js/main.js"></script>
</body>
</html>
```

---

## リキッドデザイン実装

### 基本設定

```css
/* 1rem = 10pxに設定 */
html {
  font-size: 62.5%;
}

/* 本文は16pxをベースに */
body {
  font-size: 1.6rem;
  line-height: 1.8;
}
```

### remでのサイズ指定

```css
/* pxからremへの変換: px / 10 = rem */
.element {
  font-size: 1.4rem;    /* 14px */
  padding: 2rem;        /* 20px */
  margin-bottom: 3rem;  /* 30px */
  max-width: 120rem;    /* 1200px */
}
```

### 可変幅コンテナ

```css
.l-container {
  width: 90%;              /* ビューポートの90% */
  max-width: 120rem;       /* 最大1200px */
  margin: 0 auto;
}

/* 狭いコンテナ（記事ページ用） */
.l-container--narrow {
  max-width: 80rem;        /* 最大800px */
}

/* 広いコンテナ */
.l-container--wide {
  max-width: 140rem;       /* 最大1400px */
}
```

---

## レスポンシブパターン

### ブレークポイント

```css
/* モバイルファースト */
/* 基本スタイル = モバイル */

@media (min-width: 768px) {
  /* タブレット・デスクトップ */
}

/* または デスクトップファースト */
/* 基本スタイル = デスクトップ */

@media (max-width: 767px) {
  /* モバイル */
}
```

### グリッドレイアウト

```css
/* 3カラム → 1カラム */
.p-top__feature-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3rem;
}

@media (max-width: 767px) {
  .p-top__feature-list {
    grid-template-columns: 1fr;
  }
}

/* 2カラム → 1カラム */
.p-about__content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

@media (max-width: 767px) {
  .p-about__content {
    grid-template-columns: 1fr;
  }
}
```

### フォントサイズ調整

```css
.p-top__hero-title {
  font-size: 5.6rem;
}

@media (max-width: 767px) {
  .p-top__hero-title {
    font-size: 3.2rem;
  }
}

/* clamp()を使った流動的なサイズ（オプション） */
.p-top__hero-title {
  font-size: clamp(3.2rem, 5vw, 5.6rem);
}
```

### 余白調整

```css
.p-top__hero {
  padding: 16rem 0 10rem;
}

@media (max-width: 767px) {
  .p-top__hero {
    padding: 10rem 0 6rem;
  }
}
```

### ヘッダーのレスポンシブ

```css
/* PC: 通常ナビゲーション */
.l-header__nav {
  display: flex;
  gap: 3rem;
}

.c-hamburger {
  display: none;
}

/* SP: ハンバーガーメニュー */
@media (max-width: 767px) {
  .l-header__nav {
    display: none;
    position: fixed;
    top: 6rem;
    left: 0;
    width: 100%;
    height: calc(100vh - 6rem);
    background-color: var(--color-bg);
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .l-header__nav.is-open {
    display: flex;
  }

  .c-hamburger {
    display: block;
  }
}
```

---

## よく使うCSSパターン

### センタリング

```css
/* Flexboxでセンタリング */
.center-flex {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 絶対配置でセンタリング */
.center-absolute {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
```

### アスペクト比固定

```css
.c-card__image {
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.c-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

### ホバーエフェクト

```css
/* フェードイン */
.c-button {
  transition: opacity 0.3s ease;
}

.c-button:hover {
  opacity: 0.7;
}

/* 浮き上がり */
.c-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.c-card:hover {
  transform: translateY(-0.5rem);
  box-shadow: 0 1rem 2rem rgba(0, 0, 0, 0.15);
}

/* 背景色変化 */
.c-button--primary {
  background-color: var(--color-primary);
  transition: background-color 0.3s ease;
}

.c-button--primary:hover {
  background-color: var(--color-primary-dark);
}
```

### グラデーション背景

```css
/* 線形グラデーション */
.p-top__hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 画像にオーバーレイ */
.p-top__hero {
  position: relative;
  background: url('../images/hero.jpg') center/cover no-repeat;
}

.p-top__hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
}

.p-top__hero .l-container {
  position: relative;
  z-index: 1;
}
```

### 固定ヘッダー対応

```css
/* ヘッダー分のpadding-topをbodyに */
body {
  padding-top: var(--header-height);
}

@media (max-width: 767px) {
  body {
    padding-top: 6rem; /* SP時のヘッダー高さ */
  }
}
```

---

## トラブルシューティング

### リキッドデザインが動作しない

**原因**: `font-size: 62.5%`が適用されていない

```css
/* 確認ポイント */
html {
  font-size: 62.5%; /* これが必要 */
}

/* NG: bodyに設定してもダメ */
body {
  font-size: 62.5%; /* 効果なし */
}
```

### remが大きすぎる/小さすぎる

**原因**: 親要素でfont-sizeを上書きしている

```css
/* NG: 親要素でfont-sizeを変更 */
.parent {
  font-size: 20px; /* これがあるとrem計算が狂う可能性 */
}

/* OK: htmlのfont-sizeのみ変更 */
html {
  font-size: 62.5%;
}
```

### FLOCSSの命名が混在する

**解決**: プレフィックスを必ず付ける

```css
/* NG */
.header { }
.button { }
.hero { }

/* OK */
.l-header { }   /* Layout */
.c-button { }   /* Component */
.p-top__hero { } /* Project */
```

### セクション再現の精度が低い

**確認手順**:
1. 画像を拡大して詳細確認
2. 開発者ツールで参考サイトの値を測定
3. カラーピッカーで正確な色を抽出
4. フォントサイズ・余白を数値で比較

### レスポンシブで崩れる

**チェックリスト**:
- [ ] max-widthを使っているか
- [ ] 固定幅（width: 500px等）を使っていないか
- [ ] flexboxのflex-wrapを設定しているか
- [ ] 画像にmax-width: 100%を設定しているか
- [ ] 中間サイズ（768px〜1024px）で確認したか

```css
/* 崩れにくい設定 */
img {
  max-width: 100%;
  height: auto;
}

.flex-container {
  display: flex;
  flex-wrap: wrap; /* 折り返し有効 */
}

.element {
  width: 100%;
  max-width: 50rem; /* 固定幅ではなくmax-width */
}
```

### z-indexが効かない

**原因**: positionが設定されていない

```css
/* NG */
.element {
  z-index: 100; /* positionがないと効かない */
}

/* OK */
.element {
  position: relative; /* または absolute, fixed, sticky */
  z-index: 100;
}
```

### ハンバーガーメニューが動かない

**JavaScript例**:

```javascript
// main.js
document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.querySelector('.c-hamburger');
  const nav = document.querySelector('.l-header__nav');

  if (hamburger && nav) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('is-open');
      nav.classList.toggle('is-open');
    });
  }
});
```

```css
/* ハンバーガーアイコンのCSS */
.c-hamburger {
  width: 3rem;
  height: 2rem;
  position: relative;
  cursor: pointer;
}

.c-hamburger span {
  display: block;
  width: 100%;
  height: 2px;
  background-color: var(--color-text);
  position: absolute;
  left: 0;
  transition: 0.3s ease;
}

.c-hamburger span:nth-child(1) { top: 0; }
.c-hamburger span:nth-child(2) { top: 50%; transform: translateY(-50%); }
.c-hamburger span:nth-child(3) { bottom: 0; }

/* 開いた状態 */
.c-hamburger.is-open span:nth-child(1) {
  top: 50%;
  transform: translateY(-50%) rotate(45deg);
}

.c-hamburger.is-open span:nth-child(2) {
  opacity: 0;
}

.c-hamburger.is-open span:nth-child(3) {
  bottom: 50%;
  transform: translateY(50%) rotate(-45deg);
}
```
