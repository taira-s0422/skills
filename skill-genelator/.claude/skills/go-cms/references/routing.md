# Go 1.22+ Routing Patterns

## New ServeMux Features (Go 1.22+)

Go 1.22 introduced enhanced routing with method matching and path parameters.

## Basic Patterns

```go
mux := http.NewServeMux()

// Method + Path
mux.HandleFunc("GET /posts", listPosts)
mux.HandleFunc("POST /posts", createPost)
mux.HandleFunc("GET /posts/{id}", getPost)
mux.HandleFunc("PUT /posts/{id}", updatePost)
mux.HandleFunc("DELETE /posts/{id}", deletePost)

// Exact match with {$} - matches "/" only, not "/anything"
mux.HandleFunc("GET /{$}", homeHandler)

// Wildcard - matches any suffix
mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))
```

## Path Parameters

```go
func getPost(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")  // Extract {id} from path
    // Use id...
}

// Multiple parameters
mux.HandleFunc("GET /users/{userID}/posts/{postID}", func(w http.ResponseWriter, r *http.Request) {
    userID := r.PathValue("userID")
    postID := r.PathValue("postID")
})
```

## Pattern Precedence Rules

1. More specific patterns take precedence
2. Longer patterns beat shorter ones
3. Method-specific patterns beat method-agnostic ones

```go
// These coexist without conflict:
mux.HandleFunc("GET /posts", listPosts)      // GET /posts
mux.HandleFunc("POST /posts", createPost)    // POST /posts
mux.HandleFunc("/posts/{id}", getPost)       // Any method for /posts/123
```

## Common Conflicts and Solutions

### Conflict: Root path vs prefix path

```go
// PROBLEM: Conflict between GET / and /static/
mux.Handle("/static/", staticHandler)
mux.HandleFunc("GET /", homeHandler)  // Panic!

// SOLUTION: Use {$} for exact match
mux.Handle("/static/", staticHandler)
mux.HandleFunc("GET /{$}", homeHandler)  // OK - only matches "/"
```

### Conflict: Method-specific vs method-agnostic

```go
// PROBLEM
mux.HandleFunc("/api/data", anyMethodHandler)
mux.HandleFunc("GET /api/data", getHandler)  // Panic!

// SOLUTION: Be consistent - all specific or all agnostic
mux.HandleFunc("GET /api/data", getHandler)
mux.HandleFunc("POST /api/data", postHandler)
```

## CMS Route Structure Example

```go
func SetupRoutes(mux *http.ServeMux, h *Handlers) {
    // Static files
    fs := http.FileServer(http.Dir("static"))
    mux.Handle("/static/", http.StripPrefix("/static/", fs))

    // Public routes
    mux.HandleFunc("GET /{$}", h.Home)
    mux.HandleFunc("GET /post/{slug}", h.ViewPost)
    mux.HandleFunc("GET /category/{slug}", h.ViewCategory)
    mux.HandleFunc("GET /search", h.Search)

    // Admin routes
    mux.HandleFunc("GET /admin", h.AdminDashboard)
    mux.HandleFunc("GET /admin/posts", h.AdminListPosts)
    mux.HandleFunc("GET /admin/posts/new", h.AdminNewPost)
    mux.HandleFunc("POST /admin/posts", h.AdminCreatePost)
    mux.HandleFunc("GET /admin/posts/{id}/edit", h.AdminEditPost)
    mux.HandleFunc("PUT /admin/posts/{id}", h.AdminUpdatePost)
    mux.HandleFunc("DELETE /admin/posts/{id}", h.AdminDeletePost)

    // API routes
    mux.HandleFunc("GET /api/posts", h.APIListPosts)
    mux.HandleFunc("GET /api/posts/{id}", h.APIGetPost)
    mux.HandleFunc("POST /api/posts", h.APICreatePost)
    mux.HandleFunc("PUT /api/posts/{id}", h.APIUpdatePost)
    mux.HandleFunc("DELETE /api/posts/{id}", h.APIDeletePost)
}
```

## Middleware Pattern

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if !isValidToken(token) {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}

// Usage
mux := http.NewServeMux()
// ... setup routes
handler := LoggingMiddleware(AuthMiddleware(mux))
http.ListenAndServe(":8080", handler)
```

## Route Groups with Middleware

```go
// Admin routes with auth
adminMux := http.NewServeMux()
adminMux.HandleFunc("GET /", adminDashboard)
adminMux.HandleFunc("GET /posts", adminListPosts)

// Mount with prefix and middleware
mux.Handle("/admin/", http.StripPrefix("/admin", AuthMiddleware(adminMux)))
```
