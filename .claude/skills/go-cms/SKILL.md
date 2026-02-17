---
name: go-cms
description: Go言語でフルスタックCMSを構築するためのスキル。Supabase/PostgreSQL、html/template または Templ をサポート。CMSの作成、ブログ機能の実装、管理画面の構築、API開発時に使用。「GoでCMSを作りたい」「ブログシステムを構築したい」「Go言語で管理画面を作りたい」といったリクエストで起動。
---

# Go CMS Builder

Go言語でフルスタックCMSを構築するためのガイド。

## Quick Start

```bash
# プロジェクト初期化
mkdir my-cms && cd my-cms
go mod init myapp

# 依存関係
go get github.com/lib/pq github.com/joho/godotenv github.com/google/uuid
```

## ワークフロー

### 1. プロジェクト構造の決定

プロジェクト構造の詳細は [references/structure.md](references/structure.md) を参照。

```
my-cms/
├── main.go
├── internal/
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── handlers/
│   └── middleware/
├── templates/
└── static/
```

### 2. データベース設定

Supabase接続とスキーマ設計は [references/supabase.md](references/supabase.md) を参照。

基本接続:
```go
import (
    "database/sql"
    _ "github.com/lib/pq"
)

db, _ := sql.Open("postgres", os.Getenv("DATABASE_URL"))
```

### 3. ルーティング設定

Go 1.22+のルーティングパターンは [references/routing.md](references/routing.md) を参照。

重要: `GET /` と `/static/` の競合を避けるため `GET /{$}` を使用:
```go
mux.Handle("/static/", http.StripPrefix("/static/", fs))
mux.HandleFunc("GET /{$}", homeHandler)  // 正しい
// mux.HandleFunc("GET /", homeHandler)  // 競合エラー
```

### 4. テンプレート選択

テンプレートエンジンの詳細は [references/templates.md](references/templates.md) を参照。

**html/template** (標準ライブラリ):
```go
templates := template.Must(template.ParseGlob("templates/*.html"))
templates.ExecuteTemplate(w, "home.html", data)
```

**Templ** (型安全):
```bash
go install github.com/a-h/templ/cmd/templ@latest
templ generate
```

## CMS基本機能

### CRUD Handler パターン

```go
type Handlers struct {
    db *sql.DB
}

func (h *Handlers) ListPosts(w http.ResponseWriter, r *http.Request) {
    rows, _ := h.db.Query("SELECT id, title, slug FROM posts WHERE status = 'published'")
    // ...
}

func (h *Handlers) GetPost(w http.ResponseWriter, r *http.Request) {
    slug := r.PathValue("slug")
    // ...
}

func (h *Handlers) CreatePost(w http.ResponseWriter, r *http.Request) {
    r.ParseForm()
    title := r.FormValue("title")
    // ...
}
```

### 管理画面認証 (シンプル版)

```go
func BasicAuth(next http.Handler, user, pass string) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        u, p, ok := r.BasicAuth()
        if !ok || u != user || p != pass {
            w.Header().Set("WWW-Authenticate", `Basic realm="admin"`)
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

### Markdown レンダリング

```go
import "github.com/yuin/goldmark"

func renderMarkdown(content string) string {
    var buf bytes.Buffer
    goldmark.Convert([]byte(content), &buf)
    return buf.String()
}
```

## ルート構成例

```go
// Public
mux.HandleFunc("GET /{$}", h.Home)
mux.HandleFunc("GET /post/{slug}", h.ViewPost)
mux.HandleFunc("GET /category/{slug}", h.ListByCategory)

// Admin (with auth middleware)
mux.HandleFunc("GET /admin", h.AdminDashboard)
mux.HandleFunc("GET /admin/posts", h.AdminListPosts)
mux.HandleFunc("GET /admin/posts/new", h.AdminNewPost)
mux.HandleFunc("POST /admin/posts", h.AdminCreatePost)
mux.HandleFunc("GET /admin/posts/{id}/edit", h.AdminEditPost)
mux.HandleFunc("POST /admin/posts/{id}", h.AdminUpdatePost)
mux.HandleFunc("POST /admin/posts/{id}/delete", h.AdminDeletePost)

// API
mux.HandleFunc("GET /api/posts", h.APIListPosts)
mux.HandleFunc("GET /api/posts/{id}", h.APIGetPost)
```

## 参照ドキュメント

| ファイル | 内容 |
|---------|------|
| [supabase.md](references/supabase.md) | Supabase接続、スキーマ設計、RLS、Storage |
| [routing.md](references/routing.md) | Go 1.22+ルーティング、競合解決、ミドルウェア |
| [templates.md](references/templates.md) | html/template vs Templ、継承パターン |
| [structure.md](references/structure.md) | プロジェクト構造、依存関係、設定 |
