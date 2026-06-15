-- HandoverGap RAG TiDB schema.
-- TiDB is the auditable slot/evidence/gap store, not only a vector store.

CREATE TABLE source_events (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  source_type VARCHAR(50) NOT NULL,
  source_url TEXT,
  title VARCHAR(255),
  content TEXT NOT NULL,
  actor_name VARCHAR(100),
  project_name VARCHAR(100),
  occurred_at DATETIME,
  metadata JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  scenario_id VARCHAR(32),
  subject VARCHAR(255),
  memory_type VARCHAR(50) NOT NULL,
  content TEXT NOT NULL,
  source_person_name VARCHAR(100),
  project_name VARCHAR(100),
  status VARCHAR(50) NOT NULL DEFAULT 'active',
  confidence DECIMAL(4,3),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_memory_scenario (scenario_id)
);

CREATE TABLE memory_chunks (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  source_event_id BIGINT,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  chunk_kind VARCHAR(50) NOT NULL DEFAULT 'memory',
  metadata JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_memory_chunks_item (memory_item_id),
  FULLTEXT INDEX idx_memory_chunks_content (content)
);

CREATE TABLE memory_type_schemas (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_type VARCHAR(50) NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  description TEXT,
  is_required BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_memory_type_slot (memory_type, slot_name)
);

CREATE TABLE profile_requirements (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  profile_name VARCHAR(100) NOT NULL,
  memory_type VARCHAR(50) NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  importance DECIMAL(4,3),
  reason TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_profile_memory_slot (profile_name, memory_type, slot_name)
);

CREATE TABLE memory_slots (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  slot_value TEXT,
  filled_by_source_event_id BIGINT,
  confidence DECIMAL(4,3),
  status VARCHAR(50) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_memory_slot (memory_item_id, slot_name)
);

CREATE TABLE slot_fill_attempts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  profile VARCHAR(100) NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  query_text TEXT NOT NULL,
  retrieved_event_ids JSON,
  selected_event_id BIGINT,
  fill_result TEXT,
  confidence DECIMAL(4,3),
  status VARCHAR(50) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_slot_attempt_memory_profile (memory_item_id, profile)
);

CREATE TABLE context_gaps (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  profile VARCHAR(100) NOT NULL,
  task_context TEXT,
  gap_type VARCHAR(50) NOT NULL,
  slot_name VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  severity VARCHAR(20) NOT NULL,
  required_evidence_type VARCHAR(100),
  status VARCHAR(50) NOT NULL DEFAULT 'open',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_gap_memory_profile_status (memory_item_id, profile, status)
);

CREATE TABLE clarification_questions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  context_gap_id BIGINT NOT NULL,
  question TEXT NOT NULL,
  target_person_name VARCHAR(100),
  priority VARCHAR(20),
  status VARCHAR(50) NOT NULL DEFAULT 'open',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_question_gap (context_gap_id)
);

CREATE TABLE transfer_assessments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  memory_item_id BIGINT NOT NULL,
  profile VARCHAR(100) NOT NULL,
  task_context TEXT,
  transferability_score DECIMAL(5,3) NOT NULL,
  unsafe_reason TEXT,
  required_gaps_count INT NOT NULL,
  status VARCHAR(50) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_assessment_memory_profile (memory_item_id, profile)
);

CREATE TABLE evaluation_runs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  method_name VARCHAR(100) NOT NULL,
  dataset_name VARCHAR(100) NOT NULL,
  metrics_json JSON NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
