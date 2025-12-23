-- IssueSense Database Schema
-- Execute this in Supabase SQL Editor
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
-- Teams table (create first since it's referenced by issues)
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_by UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Team members
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, user_id),
    CONSTRAINT valid_role CHECK (role IN ('owner', 'admin', 'member'))
);
-- Issues table
CREATE TABLE IF NOT EXISTS issues (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Ownership
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    -- Error Information
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    -- Context
    file_path VARCHAR(500),
    line_number INTEGER,
    function_name VARCHAR(200),
    code_snippet TEXT,
    -- Environment
    language VARCHAR(50),
    framework VARCHAR(100),
    environment VARCHAR(50),
    os VARCHAR(50),
    dependencies JSONB,
    -- Metadata
    tags TEXT [],
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'open',
    occurrences INTEGER DEFAULT 1,
    first_occurred_at TIMESTAMP DEFAULT NOW(),
    last_occurred_at TIMESTAMP DEFAULT NOW(),
    -- ML Fields
    embedding vector(384),
    embedding_text TEXT,
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- Constraints
    CONSTRAINT valid_severity CHECK (
        severity IN ('critical', 'high', 'medium', 'low')
    ),
    CONSTRAINT valid_status CHECK (status IN ('open', 'resolved', 'recurring'))
);
-- Solutions table
CREATE TABLE IF NOT EXISTS solutions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Relationships
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES auth.users(id),
    -- Solution Content
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    code_fix TEXT,
    steps TEXT [],
    -- Effectiveness Tracking
    effectiveness_score DECIMAL(3, 2) DEFAULT 0.0,
    times_used INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    -- Metadata
    tags TEXT [],
    verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMP,
    -- ML Fields
    embedding vector(384),
    embedding_text TEXT,
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Solution feedback
CREATE TABLE IF NOT EXISTS solution_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solution_id UUID NOT NULL REFERENCES solutions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    was_helpful BOOLEAN NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(solution_id, user_id)
);
-- Error occurrences (for tracking recurring errors)
CREATE TABLE IF NOT EXISTS error_occurrences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    occurred_at TIMESTAMP DEFAULT NOW(),
    context JSONB,
    resolved_with_solution_id UUID REFERENCES solutions(id)
);
-- Create indexes
CREATE INDEX IF NOT EXISTS idx_issues_user_id ON issues(user_id);
CREATE INDEX IF NOT EXISTS idx_issues_team_id ON issues(team_id);
CREATE INDEX IF NOT EXISTS idx_issues_error_type ON issues(error_type);
CREATE INDEX IF NOT EXISTS idx_issues_language ON issues(language);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity);
CREATE INDEX IF NOT EXISTS idx_issues_tags ON issues USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_issues_created_at ON issues(created_at DESC);
-- Vector similarity search index (IVFFlat)
CREATE INDEX IF NOT EXISTS idx_issues_embedding ON issues USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_solutions_issue_id ON solutions(issue_id);
CREATE INDEX IF NOT EXISTS idx_solutions_created_by ON solutions(created_by);
CREATE INDEX IF NOT EXISTS idx_solutions_effectiveness ON solutions(effectiveness_score DESC);
CREATE INDEX IF NOT EXISTS idx_solutions_verified ON solutions(verified);
CREATE INDEX IF NOT EXISTS idx_solution_feedback_solution_id ON solution_feedback(solution_id);
CREATE INDEX IF NOT EXISTS idx_error_occurrences_issue_id ON error_occurrences(issue_id);
CREATE INDEX IF NOT EXISTS idx_error_occurrences_occurred_at ON error_occurrences(occurred_at DESC);
-- Enable Row Level Security
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE solutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE solution_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE error_occurrences ENABLE ROW LEVEL SECURITY;
-- RLS Policies for issues
CREATE POLICY issues_select_policy ON issues FOR
SELECT USING (
        user_id = auth.uid()
        OR team_id IN (
            SELECT team_id
            FROM team_members
            WHERE user_id = auth.uid()
        )
    );
CREATE POLICY issues_insert_policy ON issues FOR
INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY issues_update_policy ON issues FOR
UPDATE USING (
        user_id = auth.uid()
        OR team_id IN (
            SELECT team_id
            FROM team_members
            WHERE user_id = auth.uid()
                AND role IN ('admin', 'owner')
        )
    );
CREATE POLICY issues_delete_policy ON issues FOR DELETE USING (user_id = auth.uid());
-- RLS Policies for solutions
CREATE POLICY solutions_select_policy ON solutions FOR
SELECT USING (
        issue_id IN (
            SELECT id
            FROM issues
            WHERE user_id = auth.uid()
        )
    );
CREATE POLICY solutions_insert_policy ON solutions FOR
INSERT WITH CHECK (created_by = auth.uid());
CREATE POLICY solutions_update_policy ON solutions FOR
UPDATE USING (created_by = auth.uid());
CREATE POLICY solutions_delete_policy ON solutions FOR DELETE USING (created_by = auth.uid());
-- RLS Policies for solution_feedback
CREATE POLICY solution_feedback_select_policy ON solution_feedback FOR
SELECT USING (user_id = auth.uid());
CREATE POLICY solution_feedback_insert_policy ON solution_feedback FOR
INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY solution_feedback_update_policy ON solution_feedback FOR
UPDATE USING (user_id = auth.uid());
-- RLS Policies for error_occurrences
CREATE POLICY error_occurrences_select_policy ON error_occurrences FOR
SELECT USING (
        issue_id IN (
            SELECT id
            FROM issues
            WHERE user_id = auth.uid()
        )
    );
CREATE POLICY error_occurrences_insert_policy ON error_occurrences FOR
INSERT WITH CHECK (
        issue_id IN (
            SELECT id
            FROM issues
            WHERE user_id = auth.uid()
        )
    );
-- Create helper function for vector similarity search
CREATE OR REPLACE FUNCTION match_issues(
        query_embedding vector(384),
        match_threshold float,
        match_count int,
        user_id_filter uuid
    ) RETURNS TABLE (
        id uuid,
        user_id uuid,
        error_type varchar,
        error_message text,
        stack_trace text,
        language varchar,
        framework varchar,
        tags text [],
        severity varchar,
        status varchar,
        created_at timestamp,
        distance float
    ) LANGUAGE plpgsql AS $$ BEGIN RETURN QUERY
SELECT i.id,
    i.user_id,
    i.error_type,
    i.error_message,
    i.stack_trace,
    i.language,
    i.framework,
    i.tags,
    i.severity,
    i.status,
    i.created_at,
    (i.embedding <=> query_embedding) as distance
FROM issues i
WHERE i.user_id = user_id_filter
    AND (i.embedding <=> query_embedding) < match_threshold
ORDER BY distance
LIMIT match_count;
END;
$$;
-- Comments table for issue discussions
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Comments indexes
CREATE INDEX IF NOT EXISTS idx_comments_issue_id ON comments(issue_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at DESC);
-- Enable RLS for comments
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
-- RLS Policies for comments
CREATE POLICY "Users can view comments on their issues" ON comments FOR
SELECT USING (
        issue_id IN (
            SELECT id
            FROM issues
            WHERE user_id = auth.uid()
        )
    );
CREATE POLICY "Users can create comments on their issues" ON comments FOR
INSERT WITH CHECK (
        issue_id IN (
            SELECT id
            FROM issues
            WHERE user_id = auth.uid()
        )
    );
CREATE POLICY "Users can update their own comments" ON comments FOR
UPDATE USING (user_id = auth.uid());
CREATE POLICY "Users can delete their own comments" ON comments FOR DELETE USING (user_id = auth.uid());