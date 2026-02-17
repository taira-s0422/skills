# Supabase Integration for Go

## Environment Setup

```bash
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key  # For admin operations
DATABASE_URL=postgres://user:pass@host:5432/postgres
```

## Connection Methods

### Option 1: Direct PostgreSQL (Recommended for CMS)

```go
import (
    "database/sql"
    "os"
    _ "github.com/lib/pq"
)

func InitDB() (*sql.DB, error) {
    db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        return nil, err
    }
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(5)
    return db, db.Ping()
}
```

### Option 2: Supabase REST API

```go
import (
    "bytes"
    "encoding/json"
    "net/http"
    "os"
)

type SupabaseClient struct {
    URL    string
    Key    string
    Client *http.Client
}

func NewSupabaseClient() *SupabaseClient {
    return &SupabaseClient{
        URL:    os.Getenv("SUPABASE_URL"),
        Key:    os.Getenv("SUPABASE_ANON_KEY"),
        Client: &http.Client{},
    }
}

func (s *SupabaseClient) Query(table string, query map[string]string) (*http.Response, error) {
    req, _ := http.NewRequest("GET", s.URL+"/rest/v1/"+table, nil)
    req.Header.Set("apikey", s.Key)
    req.Header.Set("Authorization", "Bearer "+s.Key)

    q := req.URL.Query()
    for k, v := range query {
        q.Add(k, v)
    }
    req.URL.RawQuery = q.Encode()

    return s.Client.Do(req)
}
```

## Database Schema for CMS

```sql
-- Posts table
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    excerpt TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    author_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ
);

-- Categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Post-Category relationship
CREATE TABLE post_categories (
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, category_id)
);

-- Media table
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    mime_type TEXT,
    size_bytes BIGINT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_updated_at
    BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

## Row Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Public can read published posts
CREATE POLICY "Public read published" ON posts
    FOR SELECT USING (status = 'published');

-- Authors can manage own posts
CREATE POLICY "Authors manage own" ON posts
    FOR ALL USING (auth.uid() = author_id);

-- Admin can manage all
CREATE POLICY "Admin manage all" ON posts
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM auth.users
            WHERE id = auth.uid()
            AND raw_user_meta_data->>'role' = 'admin'
        )
    );
```

## Storage for Media

```go
func UploadToStorage(bucket, path string, file io.Reader) error {
    client := NewSupabaseClient()

    req, _ := http.NewRequest("POST",
        client.URL+"/storage/v1/object/"+bucket+"/"+path,
        file)
    req.Header.Set("apikey", client.Key)
    req.Header.Set("Authorization", "Bearer "+client.Key)
    req.Header.Set("Content-Type", "application/octet-stream")

    resp, err := client.Client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("upload failed: %d", resp.StatusCode)
    }
    return nil
}
```
