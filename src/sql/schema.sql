CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents (id) ON DELETE CASCADE,
    kind TEXT NOT NULL, -- 'profile' | 'site-feature' | 'conversation'
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO
    agents (id, name, description)
VALUES (
        'linus_t',
        'Linus',
        'Assistente do portfólio do Matheus Braum'
    ) ON CONFLICT (id) DO NOTHING;
