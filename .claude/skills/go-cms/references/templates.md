# Template Engines for Go CMS

## Option 1: html/template (Standard Library)

### Basic Setup

```go
import (
    "html/template"
    "net/http"
)

var templates *template.Template

func init() {
    templates = template.Must(template.ParseGlob("templates/*.html"))
}

func renderTemplate(w http.ResponseWriter, name string, data any) {
    err := templates.ExecuteTemplate(w, name, data)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
    }
}
```

### Template Inheritance Pattern

```html
<!-- templates/base.html -->
{{define "base"}}
<!DOCTYPE html>
<html>
<head>
    <title>{{template "title" .}}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav>{{template "nav" .}}</nav>
    <main>{{template "content" .}}</main>
    <footer>{{template "footer" .}}</footer>
</body>
</html>
{{end}}

{{define "nav"}}
<ul>
    <li><a href="/">Home</a></li>
    <li><a href="/admin">Admin</a></li>
</ul>
{{end}}

{{define "footer"}}
<p>&copy; 2024 My CMS</p>
{{end}}
```

```html
<!-- templates/home.html -->
{{template "base" .}}

{{define "title"}}Home - My CMS{{end}}

{{define "content"}}
<h1>Welcome</h1>
{{range .Posts}}
<article>
    <h2><a href="/post/{{.Slug}}">{{.Title}}</a></h2>
    <p>{{.Excerpt}}</p>
</article>
{{end}}
{{end}}
```

### Custom Functions

```go
var funcMap = template.FuncMap{
    "formatDate": func(t time.Time) string {
        return t.Format("2006-01-02")
    },
    "truncate": func(s string, n int) string {
        if len(s) <= n {
            return s
        }
        return s[:n] + "..."
    },
    "safeHTML": func(s string) template.HTML {
        return template.HTML(s)
    },
    "markdown": func(s string) template.HTML {
        // Use goldmark or blackfriday
        return template.HTML(renderMarkdown(s))
    },
}

func init() {
    templates = template.Must(
        template.New("").Funcs(funcMap).ParseGlob("templates/*.html"),
    )
}
```

### Usage in Templates

```html
<time>{{formatDate .CreatedAt}}</time>
<p>{{truncate .Content 100}}</p>
<div class="content">{{markdown .Content}}</div>
```

---

## Option 2: Templ (Type-Safe Templates)

### Installation

```bash
go install github.com/a-h/templ/cmd/templ@latest
```

### Basic Component

```go
// templates/layout.templ
package templates

templ Layout(title string) {
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <link rel="stylesheet" href="/static/css/style.css"/>
    </head>
    <body>
        @Nav()
        <main>
            { children... }
        </main>
        @Footer()
    </body>
    </html>
}

templ Nav() {
    <nav>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/admin">Admin</a></li>
        </ul>
    </nav>
}

templ Footer() {
    <footer>
        <p>&copy; 2024 My CMS</p>
    </footer>
}
```

### Page Components

```go
// templates/home.templ
package templates

import "myapp/models"

templ Home(posts []models.Post) {
    @Layout("Home - My CMS") {
        <h1>Welcome</h1>
        for _, post := range posts {
            @PostCard(post)
        }
    }
}

templ PostCard(post models.Post) {
    <article>
        <h2><a href={templ.SafeURL("/post/" + post.Slug)}>{post.Title}</a></h2>
        <p>{post.Excerpt}</p>
        <time>{post.CreatedAt.Format("2006-01-02")}</time>
    </article>
}
```

### Generate and Use

```bash
# Generate Go code from .templ files
templ generate
```

```go
// handlers/home.go
func (h *Handlers) Home(w http.ResponseWriter, r *http.Request) {
    posts, _ := h.db.GetPublishedPosts()
    templates.Home(posts).Render(r.Context(), w)
}
```

### Conditional and Loop

```go
templ PostList(posts []models.Post, isAdmin bool) {
    for _, post := range posts {
        <article>
            <h2>{post.Title}</h2>
            if isAdmin {
                <a href={templ.SafeURL("/admin/posts/" + post.ID + "/edit")}>Edit</a>
            }
        </article>
    }
    if len(posts) == 0 {
        <p>No posts found.</p>
    }
}
```

### Raw HTML (Markdown)

```go
templ PostContent(htmlContent string) {
    <div class="content">
        @templ.Raw(htmlContent)
    </div>
}
```

---

## Choosing Between Them

| Feature | html/template | Templ |
|---------|--------------|-------|
| Setup | Zero dependencies | Requires code generation |
| Type Safety | Runtime errors | Compile-time errors |
| IDE Support | Limited | Full Go support |
| Learning Curve | Lower | Higher |
| Performance | Good | Excellent |
| Refactoring | Manual | IDE-assisted |

### Recommendation

- **html/template**: Simple projects, quick prototypes, minimal dependencies
- **Templ**: Larger projects, teams, long-term maintenance, type safety priority
