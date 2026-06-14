-- HandoverGap RAG TiDB Schema Draft
-- Canonical packaged schema: src/handovergap/data/schema.sql

CREATE TABLE source_events (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  source_type VARCHAR(50) NOT NULL,
  source_url TEXT,
  title VARCHAR(255),
  content TEXT,
  actor_name VARCHAR(100),
  project_name VARCHAR(100),
  occurred_at DATETIME,
  metadata JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  subject VARCHAR(255),
  memory_type VARCHAR(50),
  content TEXT,
  source_person_name VARCHAR(100),
  project_name VARCHAR(100),
  status VARCHAR(50),
  confidence DECIMAL(4,3),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_chunks (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT,
  content TEXT,
  embedding VECTOR(1536),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_type_schemas (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_type VARCHAR(50) NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  description TEXT,
  is_required BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE successor_role_requirements (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_name VARCHAR(100) NOT NULL,
  memory_type VARCHAR(50) NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  importance DECIMAL(4,3),
  reason TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_slots (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  slot_value TEXT,
  filled_by_source_event_id BIGINT,
  confidence DECIMAL(4,3),
  status VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE slot_fill_attempts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  query_text TEXT,
  retrieved_event_ids JSON,
  selected_event_id BIGINT,
  fill_result TEXT,
  confidence DECIMAL(4,3),
  status VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE context_gaps (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  successor_role VARCHAR(100) NOT NULL,
  task_context TEXT,
  gap_type VARCHAR(50) NOT NULL,
  slot_name VARCHAR(100),
  description TEXT,
  severity VARCHAR(20),
  required_evidence_type VARCHAR(100),
  status VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clarification_questions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  context_gap_id BIGINT NOT NULL,
  question TEXT NOT NULL,
  target_person_name VARCHAR(100),
  priority VARCHAR(20),
  status VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transfer_assessments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  successor_role VARCHAR(100) NOT NULL,
  task_context TEXT,
  transferability_score DECIMAL(5,3),
  unsafe_reason TEXT,
  required_gaps_count INT,
  status VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evaluation_runs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  method_name VARCHAR(100),
  dataset_name VARCHAR(100),
  metrics_json JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
