CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    CHECK (name IN ('ice bath', 'hot wings', 'treadmill'))
);

CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    challenge_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    answers TEXT[] NOT NULL,
    likes INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    submission_id INT NOT NULL,
    author VARCHAR(40) NOT NULL DEFAULT 'Anonymous',
    body VARCHAR(280) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (submission_id) REFERENCES submissions(id)
);

CREATE INDEX idx_comments_submission ON comments(submission_id);

CREATE TABLE nominations (
    id SERIAL PRIMARY KEY,
    submission_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    FOREIGN KEY (submission_id) REFERENCES submissions(id)
);

INSERT INTO challenges (name) VALUES
    ('ice bath'),
    ('hot wings'),
    ('treadmill');