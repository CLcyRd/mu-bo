CREATE TABLE IF NOT EXISTS consultation (
  id BIGINT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  cover VARCHAR(1024) NOT NULL DEFAULT '',
  content LONGTEXT NOT NULL,
  author_id BIGINT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  status TINYINT NOT NULL DEFAULT 0,
  CONSTRAINT fk_consultation_author FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE INDEX idx_consultation_title ON consultation(title);
CREATE FULLTEXT INDEX ftx_consultation_title ON consultation(title);
CREATE INDEX idx_consultation_author_status_created ON consultation(author_id, status, created_at);

CREATE TABLE IF NOT EXISTS consultation_versions (
  id BIGINT PRIMARY KEY,
  consultation_id BIGINT NOT NULL,
  version_no INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  content LONGTEXT NOT NULL,
  editor_id BIGINT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_consultation_versions_consultation FOREIGN KEY (consultation_id) REFERENCES consultation(id),
  CONSTRAINT fk_consultation_versions_editor FOREIGN KEY (editor_id) REFERENCES users(id),
  CONSTRAINT uq_consultation_versions UNIQUE (consultation_id, version_no)
);

CREATE TABLE IF NOT EXISTS consultation_idempotency (
  id BIGINT PRIMARY KEY,
  idempotency_key VARCHAR(128) NOT NULL,
  endpoint VARCHAR(128) NOT NULL,
  author_id BIGINT NOT NULL,
  request_hash VARCHAR(64) NOT NULL,
  response_body LONGTEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_consultation_idempotency_author FOREIGN KEY (author_id) REFERENCES users(id),
  CONSTRAINT uq_consultation_idempotency UNIQUE (idempotency_key, author_id)
);
