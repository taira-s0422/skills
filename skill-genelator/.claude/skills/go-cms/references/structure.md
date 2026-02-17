# Go CMS Project Structure

## Recommended Directory Layout

```
my-cms/
├── main.go                 # Entry point
├── go.mod
├── go.sum
├── .env                    # Environment variables (gitignored)
├── .env.example            # Template for environment variables
│
├── internal/               # Private application code
│   ├── config/
│   │   └── config.go       # Configuration loading
│   │
│   ├── database/
│   │   ├── database.go     # DB connection
│   │   └── migrations/     # SQL migration files
│   │
│   ├── models/
│   │   ├── post.go
│   │   ├── category.go
│   │   ├── user.go
│   │   └── media.go
│   │
│   ├── handlers/
│   │   ├── handlers.go     # Handler struct with dependencies
│   │   ├── home.go
│   │   ├── post.go
│   │   ├── admin.go
│   │   └── api.go
│   │
│   ├── middleware/
│   │   ├── logging.go
│   │   ├── auth.go
│   │   └── cors.go
│   │
│   └── services/           # Business logic (optional)
│       ├── post_service.go
│       └── auth_service.go
│
├── templates/              # html/template files
│   ├── base.html
│   ├── home.html
│   ├── post.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── posts.html
│   │   └── edit.html
│   └── partials/
│       ├── header.html
│       └── footer.html
│
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
└── uploads/                # User uploads (gitignored)
```

## Alternative: Templ-based Structure

```
my-cms/
├── main.go
├── go.mod
│
├── internal/
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── handlers/
│   └── middleware/
│
├── templates/              # Templ components
│   ├── layout.templ
│   ├── components/
│   │   ├── nav.templ
│   │   ├── footer.templ
│   │   └── post_card.templ
│   ├── pages/
│   │   ├── home.templ
│   │   └── post.templ
│   └── admin/
│       ├── dashboard.templ
│       └── posts.templ
│
└── static/
```

## Key Files

### main.go

```go
package main

import (
    "log"
    "net/http"

    "myapp/internal/config"
    "myapp/internal/database"
    "myapp/internal/handlers"
    "myapp/internal/middleware"
)

func main() {
    cfg := config.Load()
    db := database.Connect(cfg.DatabaseURL)
    defer db.Close()

    h := handlers.New(db)
    mux := http.NewServeMux()

    // Static files
    fs := http.FileServer(http.Dir("static"))
    mux.Handle("/static/", http.StripPrefix("/static/", fs))

    // Routes
    setupRoutes(mux, h)

    // Middleware chain
    handler := middleware.Logging(middleware.Recovery(mux))

    log.Printf("Server starting on %s", cfg.Port)
    log.Fatal(http.ListenAndServe(":"+cfg.Port, handler))
}
```

### internal/config/config.go

```go
package config

import (
    "os"

    "github.com/joho/godotenv"
)

type Config struct {
    Port        string
    DatabaseURL string
    SupabaseURL string
    SupabaseKey string
    JWTSecret   string
}

func Load() *Config {
    godotenv.Load() // Load .env file

    return &Config{
        Port:        getEnv("PORT", "8080"),
        DatabaseURL: os.Getenv("DATABASE_URL"),
        SupabaseURL: os.Getenv("SUPABASE_URL"),
        SupabaseKey: os.Getenv("SUPABASE_ANON_KEY"),
        JWTSecret:   os.Getenv("JWT_SECRET"),
    }
}

func getEnv(key, fallback string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return fallback
}
```

### internal/handlers/handlers.go

```go
package handlers

import (
    "database/sql"
    "html/template"
)

type Handlers struct {
    db        *sql.DB
    templates *template.Template
}

func New(db *sql.DB) *Handlers {
    tmpl := template.Must(template.ParseGlob("templates/**/*.html"))
    return &Handlers{
        db:        db,
        templates: tmpl,
    }
}

func (h *Handlers) render(w http.ResponseWriter, name string, data any) {
    if err := h.templates.ExecuteTemplate(w, name, data); err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
    }
}
```

### internal/models/post.go

```go
package models

import "time"

type Post struct {
    ID          string
    Title       string
    Slug        string
    Content     string
    Excerpt     string
    Status      string // draft, published, archived
    AuthorID    string
    CreatedAt   time.Time
    UpdatedAt   time.Time
    PublishedAt *time.Time
}

type PostRepository interface {
    GetByID(id string) (*Post, error)
    GetBySlug(slug string) (*Post, error)
    GetPublished(limit, offset int) ([]Post, error)
    Create(post *Post) error
    Update(post *Post) error
    Delete(id string) error
}
```

## Dependencies (go.mod)

```
module myapp

go 1.22

require (
    github.com/lib/pq v1.10.9              // PostgreSQL driver
    github.com/joho/godotenv v1.5.1        // .env loading
    github.com/google/uuid v1.6.0          // UUID generation
    github.com/yuin/goldmark v1.7.0        // Markdown rendering
)

// Optional for Templ
require github.com/a-h/templ v0.2.543
```

## Quick Start Commands

```bash
# Initialize project
mkdir my-cms && cd my-cms
go mod init myapp

# Install dependencies
go get github.com/lib/pq
go get github.com/joho/godotenv
go get github.com/google/uuid

# For Templ (optional)
go install github.com/a-h/templ/cmd/templ@latest
go get github.com/a-h/templ

# Run
go run main.go

# Build
go build -o cms main.go
```
