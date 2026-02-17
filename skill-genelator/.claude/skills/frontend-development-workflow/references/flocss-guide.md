# FLOCSS詳細ガイド

## 目次
- [ディレクトリ構造](#ディレクトリ構造)
- [Foundation](#foundation)
- [Layout](#layout)
- [Object - Component](#object---component)
- [Object - Project](#object---project)
- [Object - Utility](#object---utility)
- [BEM記法との組み合わせ](#bem記法との組み合わせ)

---

## ディレクトリ構造

```
css/
├── style.css              # メインCSS（全てをインポート）
├── foundation/
│   ├── _reset.css         # リセットCSS
│   ├── _base.css          # 基本スタイル（html, body, 共通要素）
│   └── _variables.css     # CSS変数定義
├── layout/
│   ├── _header.css        # l-header
│   ├── _footer.css        # l-footer
│   ├── _sidebar.css       # l-sidebar
│   └── _container.css     # l-container
└── object/
    ├── component/         # 再利用可能なコンポーネント
    │   ├── _button.css    # c-button
    │   ├── _card.css      # c-card
    │   ├── _heading.css   # c-heading
    │   └── _form.css      # c-form
    ├── project/           # ページ固有のスタイル
    │   ├── _top.css       # p-top
    │   ├── _about.css     # p-about
    │   └── _contact.css   # p-contact
    └── utility/           # 汎用クラス
        ├── _margin.css    # u-mt-*, u-mb-*
        ├── _text.css      # u-text-*
        └── _display.css   # u-block, u-none
```

### style.css（インポート順序）

```css
/* ==========================================================================
   Foundation
   ========================================================================== */
@import 'foundation/_reset.css';
@import 'foundation/_variables.css';
@import 'foundation/_base.css';

/* ==========================================================================
   Layout
   ========================================================================== */
@import 'layout/_header.css';
@import 'layout/_footer.css';
@import 'layout/_sidebar.css';
@import 'layout/_container.css';

/* ==========================================================================
   Object - Component
   ========================================================================== */
@import 'object/component/_button.css';
@import 'object/component/_card.css';
@import 'object/component/_heading.css';
@import 'object/component/_form.css';

/* ==========================================================================
   Object - Project
   ========================================================================== */
@import 'object/project/_top.css';
@import 'object/project/_about.css';
@import 'object/project/_contact.css';

/* ==========================================================================
   Object - Utility
   ========================================================================== */
@import 'object/utility/_margin.css';
@import 'object/utility/_text.css';
@import 'object/utility/_display.css';
```

---

## Foundation

接頭辞なし。サイト全体の基礎スタイルを定義。

### _variables.css

```css
:root {
  /* Colors */
  --color-primary: #3498db;
  --color-primary-dark: #2980b9;
  --color-secondary: #2ecc71;
  --color-accent: #e74c3c;
  --color-text: #333333;
  --color-text-light: #666666;
  --color-bg: #ffffff;
  --color-bg-gray: #f5f5f5;
  --color-border: #dddddd;

  /* Spacing */
  --space-xs: 0.5rem;   /* 5px */
  --space-sm: 1rem;     /* 10px */
  --space-md: 2rem;     /* 20px */
  --space-lg: 4rem;     /* 40px */
  --space-xl: 8rem;     /* 80px */
  --space-xxl: 12rem;   /* 120px */

  /* Typography */
  --font-base: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif;
  --font-heading: 'Montserrat', sans-serif;
  --font-size-xs: 1.2rem;   /* 12px */
  --font-size-sm: 1.4rem;   /* 14px */
  --font-size-base: 1.6rem; /* 16px */
  --font-size-lg: 1.8rem;   /* 18px */
  --font-size-xl: 2.4rem;   /* 24px */
  --font-size-2xl: 3.2rem;  /* 32px */
  --font-size-3xl: 4.8rem;  /* 48px */

  /* Layout */
  --max-width: 120rem;      /* 1200px */
  --header-height: 8rem;    /* 80px */

  /* Transition */
  --transition-base: 0.3s ease;
  --transition-slow: 0.5s ease;

  /* Border Radius */
  --radius-sm: 0.4rem;
  --radius-md: 0.8rem;
  --radius-lg: 1.6rem;
  --radius-full: 50%;

  /* Shadow */
  --shadow-sm: 0 0.2rem 0.4rem rgba(0, 0, 0, 0.1);
  --shadow-md: 0 0.4rem 0.8rem rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 0.8rem 1.6rem rgba(0, 0, 0, 0.1);
}
```

### _reset.css

```css
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 62.5%; /* 1rem = 10px */
}

body {
  line-height: 1;
  -webkit-font-smoothing: antialiased;
}

img,
picture,
video,
canvas,
svg {
  display: block;
  max-width: 100%;
}

input,
button,
textarea,
select {
  font: inherit;
}

p,
h1,
h2,
h3,
h4,
h5,
h6 {
  overflow-wrap: break-word;
}

a {
  color: inherit;
  text-decoration: none;
}

ul,
ol {
  list-style: none;
}

button {
  background: none;
  border: none;
  cursor: pointer;
}
```

### _base.css

```css
body {
  font-family: var(--font-base);
  font-size: var(--font-size-base);
  line-height: 1.8;
  color: var(--color-text);
  background-color: var(--color-bg);
}

a {
  transition: var(--transition-base);
}

a:hover {
  opacity: 0.7;
}

img {
  height: auto;
}
```

---

## Layout

`l-` 接頭辞。ページ全体のレイアウト構造を定義。

### _header.css

```css
.l-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: var(--header-height);
  background-color: var(--color-bg);
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.l-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.l-header__logo {
  font-size: var(--font-size-xl);
  font-weight: bold;
}

.l-header__nav {
  display: flex;
  gap: var(--space-lg);
}

.l-header__nav-item {
  font-size: var(--font-size-sm);
}

@media (max-width: 767px) {
  .l-header {
    height: 6rem;
  }

  .l-header__nav {
    display: none;
  }
}
```

### _container.css

```css
.l-container {
  width: 90%;
  max-width: var(--max-width);
  margin: 0 auto;
}

.l-container--narrow {
  max-width: 80rem; /* 800px */
}

.l-container--wide {
  max-width: 140rem; /* 1400px */
}
```

### _footer.css

```css
.l-footer {
  background-color: var(--color-text);
  color: var(--color-bg);
  padding: var(--space-xl) 0;
}

.l-footer__inner {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-lg);
}

.l-footer__copyright {
  width: 100%;
  text-align: center;
  font-size: var(--font-size-sm);
  margin-top: var(--space-lg);
  padding-top: var(--space-md);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

@media (max-width: 767px) {
  .l-footer__inner {
    flex-direction: column;
  }
}
```

---

## Object - Component

`c-` 接頭辞。サイト全体で再利用可能なコンポーネント。

### _button.css

```css
.c-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 3rem;
  font-size: var(--font-size-base);
  font-weight: bold;
  text-align: center;
  border-radius: var(--radius-md);
  transition: var(--transition-base);
  cursor: pointer;
}

/* モディファイア */
.c-button--primary {
  background-color: var(--color-primary);
  color: #fff;
}

.c-button--primary:hover {
  background-color: var(--color-primary-dark);
}

.c-button--secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.c-button--secondary:hover {
  background-color: var(--color-primary);
  color: #fff;
}

.c-button--large {
  padding: 2rem 4rem;
  font-size: var(--font-size-lg);
}

.c-button--small {
  padding: 1rem 2rem;
  font-size: var(--font-size-sm);
}

.c-button--full {
  width: 100%;
}

/* エレメント */
.c-button__icon {
  margin-right: 0.8rem;
}
```

### _card.css

```css
.c-card {
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: var(--transition-base);
}

.c-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-0.5rem);
}

.c-card__image {
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.c-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.c-card__body {
  padding: var(--space-md);
}

.c-card__title {
  font-size: var(--font-size-lg);
  font-weight: bold;
  margin-bottom: var(--space-sm);
}

.c-card__text {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  line-height: 1.6;
}

.c-card__footer {
  padding: var(--space-sm) var(--space-md);
  border-top: 1px solid var(--color-border);
}
```

### _heading.css

```css
.c-heading {
  font-family: var(--font-heading);
  font-weight: bold;
  line-height: 1.4;
}

.c-heading--h2 {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--space-lg);
}

.c-heading--h3 {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--space-md);
}

.c-heading--h4 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--space-sm);
}

.c-heading--center {
  text-align: center;
}

.c-heading__sub {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  margin-bottom: var(--space-xs);
  font-weight: normal;
}

@media (max-width: 767px) {
  .c-heading--h2 {
    font-size: var(--font-size-2xl);
  }

  .c-heading--h3 {
    font-size: var(--font-size-xl);
  }

  .c-heading--h4 {
    font-size: var(--font-size-lg);
  }
}
```

---

## Object - Project

`p-` 接頭辞。特定のページやセクションに固有のスタイル。

### _top.css（例）

```css
/* ヒーローセクション */
.p-top__hero {
  padding: 16rem 0 10rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  text-align: center;
}

.p-top__hero-title {
  font-size: 5.6rem;
  font-weight: bold;
  margin-bottom: var(--space-md);
}

.p-top__hero-subtitle {
  font-size: var(--font-size-xl);
  margin-bottom: var(--space-lg);
  opacity: 0.9;
}

/* 特徴セクション */
.p-top__feature {
  padding: var(--space-xxl) 0;
}

.p-top__feature-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

.p-top__feature-item {
  text-align: center;
  padding: var(--space-lg);
}

.p-top__feature-icon {
  font-size: 4.8rem;
  color: var(--color-primary);
  margin-bottom: var(--space-md);
}

/* CTAセクション */
.p-top__cta {
  padding: var(--space-xxl) 0;
  background-color: var(--color-bg-gray);
  text-align: center;
}

@media (max-width: 767px) {
  .p-top__hero {
    padding: 12rem 0 6rem;
  }

  .p-top__hero-title {
    font-size: 3.2rem;
  }

  .p-top__feature-list {
    grid-template-columns: 1fr;
  }
}
```

---

## Object - Utility

`u-` 接頭辞。単一目的の汎用クラス。

### _margin.css

```css
/* Margin Top */
.u-mt-0 { margin-top: 0; }
.u-mt-10 { margin-top: 1rem; }
.u-mt-20 { margin-top: 2rem; }
.u-mt-30 { margin-top: 3rem; }
.u-mt-40 { margin-top: 4rem; }
.u-mt-50 { margin-top: 5rem; }
.u-mt-60 { margin-top: 6rem; }
.u-mt-80 { margin-top: 8rem; }
.u-mt-100 { margin-top: 10rem; }

/* Margin Bottom */
.u-mb-0 { margin-bottom: 0; }
.u-mb-10 { margin-bottom: 1rem; }
.u-mb-20 { margin-bottom: 2rem; }
.u-mb-30 { margin-bottom: 3rem; }
.u-mb-40 { margin-bottom: 4rem; }
.u-mb-50 { margin-bottom: 5rem; }
.u-mb-60 { margin-bottom: 6rem; }
.u-mb-80 { margin-bottom: 8rem; }
.u-mb-100 { margin-bottom: 10rem; }

/* Padding */
.u-pt-0 { padding-top: 0; }
.u-pt-20 { padding-top: 2rem; }
.u-pt-40 { padding-top: 4rem; }
.u-pt-60 { padding-top: 6rem; }
.u-pt-80 { padding-top: 8rem; }

.u-pb-0 { padding-bottom: 0; }
.u-pb-20 { padding-bottom: 2rem; }
.u-pb-40 { padding-bottom: 4rem; }
.u-pb-60 { padding-bottom: 6rem; }
.u-pb-80 { padding-bottom: 8rem; }
```

### _text.css

```css
/* Text Align */
.u-text-center { text-align: center; }
.u-text-left { text-align: left; }
.u-text-right { text-align: right; }

/* Font Weight */
.u-text-bold { font-weight: bold; }
.u-text-normal { font-weight: normal; }

/* Font Size */
.u-text-xs { font-size: var(--font-size-xs); }
.u-text-sm { font-size: var(--font-size-sm); }
.u-text-base { font-size: var(--font-size-base); }
.u-text-lg { font-size: var(--font-size-lg); }
.u-text-xl { font-size: var(--font-size-xl); }

/* Color */
.u-text-primary { color: var(--color-primary); }
.u-text-secondary { color: var(--color-secondary); }
.u-text-light { color: var(--color-text-light); }
.u-text-white { color: #fff; }
```

### _display.css

```css
.u-block { display: block; }
.u-inline-block { display: inline-block; }
.u-flex { display: flex; }
.u-grid { display: grid; }
.u-none { display: none; }

/* Visibility */
.u-visible { visibility: visible; }
.u-hidden { visibility: hidden; }

/* レスポンシブ表示切替 */
.u-sp-only {
  display: none;
}

.u-pc-only {
  display: block;
}

@media (max-width: 767px) {
  .u-sp-only {
    display: block;
  }

  .u-pc-only {
    display: none;
  }
}
```

---

## BEM記法との組み合わせ

FLOCSSでは、Block__Element--Modifierの命名規則を使用。

```
[プレフィックス]-[Block]__[Element]--[Modifier]
```

### 例

```css
/* Block */
.c-card { }

/* Element（Blockの構成要素） */
.c-card__image { }
.c-card__title { }
.c-card__body { }

/* Modifier（バリエーション） */
.c-card--featured { }
.c-card--horizontal { }

/* Elementのモディファイア */
.c-card__title--large { }
```

### HTML例

```html
<article class="c-card c-card--featured">
  <div class="c-card__image">
    <img src="..." alt="">
  </div>
  <div class="c-card__body">
    <h3 class="c-card__title c-card__title--large">タイトル</h3>
    <p class="c-card__text">テキスト</p>
  </div>
</article>
```

### 命名のポイント

1. **Block**: 独立したコンポーネント単位
2. **Element**: Blockに依存する構成要素（`__`で接続）
3. **Modifier**: 状態やバリエーション（`--`で接続）
4. **孫要素は作らない**: `__element__child` は避け、`__element-child` とする
