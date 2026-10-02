-- Reference design only. Not installed into runtime or the legacy database.
-- Implement through versioned migrations; see 04_DATA_API.md.
PRAGMA foreign_keys = ON;
CREATE TABLE repair_orgs(id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE repair_projects(
 id TEXT PRIMARY KEY, org_id TEXT NOT NULL REFERENCES repair_orgs(id), name TEXT NOT NULL,
 authority_mode TEXT NOT NULL DEFAULT 'LOCAL' CHECK(authority_mode='LOCAL'), UNIQUE(id,org_id));
CREATE TABLE repair_users(
 id TEXT PRIMARY KEY, org_id TEXT NOT NULL REFERENCES repair_orgs(id), username TEXT NOT NULL,
 display_name TEXT NOT NULL, password_hash TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1 CHECK(active IN(0,1)),
 UNIQUE(org_id,username), UNIQUE(id,org_id));
CREATE TABLE repair_user_project_roles(
 user_id TEXT NOT NULL, project_id TEXT NOT NULL, org_id TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN('REPORTER','TECHNICIAN','MANAGER')),
 PRIMARY KEY(user_id,project_id,role),
 FOREIGN KEY(user_id,org_id) REFERENCES repair_users(id,org_id),
 FOREIGN KEY(project_id,org_id) REFERENCES repair_projects(id,org_id));
CREATE TABLE repair_user_skills(
 user_id TEXT NOT NULL REFERENCES repair_users(id), skill TEXT NOT NULL,
 PRIMARY KEY(user_id,skill));
CREATE TABLE repair_spaces(
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES repair_projects(id), code TEXT NOT NULL,
 name TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1 CHECK(active IN(0,1)),
 source TEXT NOT NULL CHECK(source IN('DEMO','LOCAL_IMPORT','EXTERNAL_SNAPSHOT')), source_ref TEXT,
 UNIQUE(project_id,code), UNIQUE(id,project_id));
CREATE TABLE repair_assets(
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES repair_projects(id), asset_code TEXT NOT NULL,
 display_name TEXT NOT NULL, category TEXT NOT NULL, installation_space_id TEXT,
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN(0,1)),
 source TEXT NOT NULL CHECK(source IN('DEMO','LOCAL_IMPORT','EXTERNAL_SNAPSHOT')), source_ref TEXT,
 source_updated_at_ms INTEGER, captured_at_ms INTEGER NOT NULL,
 UNIQUE(project_id,asset_code), UNIQUE(id,project_id),
 FOREIGN KEY(installation_space_id,project_id) REFERENCES repair_spaces(id,project_id));
CREATE TABLE repair_asset_serves(
 asset_id TEXT NOT NULL, space_id TEXT NOT NULL, project_id TEXT NOT NULL,
 valid_from_ms INTEGER NOT NULL, valid_to_ms INTEGER,
 PRIMARY KEY(asset_id,space_id,valid_from_ms), CHECK(valid_to_ms IS NULL OR valid_to_ms>valid_from_ms),
 FOREIGN KEY(asset_id,project_id) REFERENCES repair_assets(id,project_id),
 FOREIGN KEY(space_id,project_id) REFERENCES repair_spaces(id,project_id));
CREATE TABLE repair_tasks(
 id TEXT PRIMARY KEY, task_no TEXT NOT NULL UNIQUE, project_id TEXT NOT NULL REFERENCES repair_projects(id),
 reporter_id TEXT NOT NULL REFERENCES repair_users(id), assignee_id TEXT REFERENCES repair_users(id),
 space_id TEXT, asset_id TEXT, previous_task_id TEXT,
 status TEXT NOT NULL CHECK(status IN('DRAFT','OPEN','ACCEPTED','SCHEDULED','IN_PROGRESS','AWAITING_ACCEPTANCE','COMPLETED','CANCELLED')),
 version INTEGER NOT NULL DEFAULT 1 CHECK(version>=1), raw_text TEXT NOT NULL,
 summary TEXT, symptom TEXT CHECK(symptom IN('HVAC_NOT_COOLING','WATER_LEAK','ELECTRICAL','OTHER')),
 contact_name TEXT, contact_detail TEXT, requested_start_ms INTEGER, requested_end_ms INTEGER,
 source_kind TEXT NOT NULL DEFAULT 'USER', source_event_id TEXT,
 external_sync_state TEXT NOT NULL DEFAULT 'NOT_CONFIGURED' CHECK(external_sync_state IN('NOT_CONFIGURED','PENDING','SUCCEEDED','FAILED','UNKNOWN')),
 created_at_ms INTEGER NOT NULL, updated_at_ms INTEGER NOT NULL,
 UNIQUE(id,project_id),
 FOREIGN KEY(space_id,project_id) REFERENCES repair_spaces(id,project_id),
 FOREIGN KEY(asset_id,project_id) REFERENCES repair_assets(id,project_id),
 FOREIGN KEY(previous_task_id,project_id) REFERENCES repair_tasks(id,project_id),
 CHECK((requested_start_ms IS NULL AND requested_end_ms IS NULL) OR
       (requested_start_ms IS NOT NULL AND requested_end_ms IS NOT NULL AND requested_end_ms>requested_start_ms)),
 CHECK(status NOT IN('ACCEPTED','SCHEDULED','IN_PROGRESS','AWAITING_ACCEPTANCE','COMPLETED') OR assignee_id IS NOT NULL),
 CHECK(status NOT IN('IN_PROGRESS','AWAITING_ACCEPTANCE','COMPLETED') OR asset_id IS NOT NULL));
CREATE UNIQUE INDEX repair_source_event_unique ON repair_tasks(project_id,reporter_id,source_kind,source_event_id) WHERE source_event_id IS NOT NULL;
CREATE INDEX repair_task_list ON repair_tasks(project_id,status,updated_at_ms,id);
CREATE INDEX repair_task_reporter ON repair_tasks(reporter_id,updated_at_ms,id);
CREATE TABLE repair_actions(
 id TEXT PRIMARY KEY, org_id TEXT NOT NULL REFERENCES repair_orgs(id), actor_id TEXT NOT NULL,
 actor_kind TEXT NOT NULL CHECK(actor_kind IN('USER','SYSTEM')), task_id TEXT REFERENCES repair_tasks(id),
 idempotency_key TEXT NOT NULL, request_hash TEXT NOT NULL, command_type TEXT NOT NULL,
 expected_version INTEGER, status TEXT NOT NULL CHECK(status IN('SUCCEEDED','REJECTED','FAILED')),
 result_json TEXT NOT NULL CHECK(json_valid(result_json)), created_at_ms INTEGER NOT NULL,
 UNIQUE(org_id,actor_id,idempotency_key));
CREATE TABLE repair_appointments(
 id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES repair_tasks(id), technician_id TEXT NOT NULL REFERENCES repair_users(id),
 start_at_ms INTEGER NOT NULL, end_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL,
 status TEXT NOT NULL CHECK(status IN('PROPOSED','CONFIRMED','REJECTED','EXPIRED','SUPERSEDED','CANCELLED')),
 version INTEGER NOT NULL DEFAULT 1 CHECK(version>=1), proposed_by TEXT NOT NULL REFERENCES repair_users(id),
 confirmed_by TEXT REFERENCES repair_users(id), note TEXT, reason TEXT,
 created_at_ms INTEGER NOT NULL, updated_at_ms INTEGER NOT NULL,
 CHECK(end_at_ms>start_at_ms), CHECK(status!='CONFIRMED' OR confirmed_by IS NOT NULL));
CREATE UNIQUE INDEX repair_one_proposal ON repair_appointments(task_id) WHERE status='PROPOSED';
CREATE UNIQUE INDEX repair_one_confirmation ON repair_appointments(task_id) WHERE status='CONFIRMED';
CREATE INDEX repair_tech_schedule ON repair_appointments(technician_id,status,start_at_ms,end_at_ms);
-- Half-open intervals; conflict checks cover all projects for a technician.
CREATE TRIGGER repair_appointment_overlap_insert BEFORE INSERT ON repair_appointments
 WHEN NEW.status='CONFIRMED'
 BEGIN SELECT RAISE(ABORT,'SLOT_CONFLICT') WHERE EXISTS(
  SELECT 1 FROM repair_appointments a WHERE a.technician_id=NEW.technician_id AND a.status='CONFIRMED'
  AND a.start_at_ms<NEW.end_at_ms AND a.end_at_ms>NEW.start_at_ms); END;
CREATE TRIGGER repair_appointment_overlap_update BEFORE UPDATE OF status,start_at_ms,end_at_ms,technician_id ON repair_appointments
 WHEN NEW.status='CONFIRMED'
 BEGIN SELECT RAISE(ABORT,'SLOT_CONFLICT') WHERE EXISTS(
  SELECT 1 FROM repair_appointments a WHERE a.id!=NEW.id AND a.technician_id=NEW.technician_id AND a.status='CONFIRMED'
  AND a.start_at_ms<NEW.end_at_ms AND a.end_at_ms>NEW.start_at_ms); END;
CREATE TABLE repair_attachments(
 id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES repair_tasks(id), uploaded_by TEXT NOT NULL REFERENCES repair_users(id),
 storage_key TEXT NOT NULL UNIQUE, original_name TEXT NOT NULL, media_type TEXT NOT NULL CHECK(media_type IN('image/jpeg','image/png','application/pdf')),
 size_bytes INTEGER NOT NULL CHECK(size_bytes>0 AND size_bytes<=10485760), sha256 TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN('READY','QUARANTINED','DELETED')), created_at_ms INTEGER NOT NULL,
 UNIQUE(id,task_id));
CREATE TABLE repair_progress(
 id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES repair_tasks(id), actor_id TEXT NOT NULL REFERENCES repair_users(id),
 kind TEXT NOT NULL CHECK(kind IN('INSPECTION','REPAIR','WAITING_PARTS','NOTE')),
 note TEXT NOT NULL CHECK(length(note)>0), attachment_ids_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(attachment_ids_json)),
 created_at_ms INTEGER NOT NULL);
CREATE TABLE repair_completions(
 id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES repair_tasks(id), author_id TEXT NOT NULL REFERENCES repair_users(id),
 resolution TEXT NOT NULL CHECK(length(resolution)>0), actual_root_cause TEXT NOT NULL,
 created_at_ms INTEGER NOT NULL, UNIQUE(id,task_id));
CREATE TABLE repair_completion_attachments(
 completion_id TEXT NOT NULL, attachment_id TEXT NOT NULL, task_id TEXT NOT NULL,
 PRIMARY KEY(completion_id,attachment_id),
 FOREIGN KEY(completion_id,task_id) REFERENCES repair_completions(id,task_id),
 FOREIGN KEY(attachment_id,task_id) REFERENCES repair_attachments(id,task_id));
CREATE TABLE repair_acceptances(
 id TEXT PRIMARY KEY, task_id TEXT NOT NULL, completion_id TEXT NOT NULL UNIQUE,
 actor_id TEXT NOT NULL REFERENCES repair_users(id), outcome TEXT NOT NULL CHECK(outcome IN('ACCEPTED','REJECTED')),
 on_behalf INTEGER NOT NULL DEFAULT 0 CHECK(on_behalf IN(0,1)), note TEXT,
 created_at_ms INTEGER NOT NULL,
 FOREIGN KEY(completion_id,task_id) REFERENCES repair_completions(id,task_id),
 CHECK((outcome!='REJECTED' AND on_behalf=0) OR length(trim(coalesce(note,'')))>0));
CREATE TABLE repair_events(
 seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE, task_id TEXT NOT NULL REFERENCES repair_tasks(id),
 task_version INTEGER NOT NULL, actor_id TEXT NOT NULL, actor_kind TEXT NOT NULL CHECK(actor_kind IN('USER','SYSTEM')),
 action_id TEXT REFERENCES repair_actions(id), type TEXT NOT NULL, payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
 created_at_ms INTEGER NOT NULL, UNIQUE(task_id,task_version));
CREATE TABLE repair_notifications(
 id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES repair_events(event_id), recipient_id TEXT NOT NULL REFERENCES repair_users(id),
 kind TEXT NOT NULL, task_id TEXT NOT NULL REFERENCES repair_tasks(id), created_at_ms INTEGER NOT NULL, read_at_ms INTEGER,
 UNIQUE(event_id,recipient_id,kind));
CREATE TABLE repair_pins(
 user_id TEXT NOT NULL REFERENCES repair_users(id), task_id TEXT NOT NULL REFERENCES repair_tasks(id), created_at_ms INTEGER NOT NULL,
 PRIMARY KEY(user_id,task_id));
CREATE TABLE repair_jobs(
 id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN('RUN_AGENT','EXPIRE_APPOINTMENT','REMIND_APPOINTMENT','REMIND_ACCEPTANCE','DISPATCH_NOTIFICATION')),
 dedup_key TEXT NOT NULL UNIQUE, object_id TEXT NOT NULL, object_version INTEGER,
 due_at_ms INTEGER NOT NULL, state TEXT NOT NULL CHECK(state IN('PENDING','RUNNING','SUCCEEDED','FAILED','CANCELLED')),
 lease_owner TEXT, lease_until_ms INTEGER, attempts INTEGER NOT NULL DEFAULT 0,
 payload_json TEXT NOT NULL CHECK(json_valid(payload_json)), last_error TEXT);
CREATE INDEX repair_jobs_due ON repair_jobs(state,due_at_ms);
CREATE TABLE repair_agent_runs(
 id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES repair_tasks(id), requested_by TEXT NOT NULL REFERENCES repair_users(id),
 base_task_version INTEGER NOT NULL, purpose TEXT NOT NULL CHECK(purpose IN('DRAFT_ASSIST','REPAIR_ADVICE','PROGRESS_SUMMARY')),
 state TEXT NOT NULL CHECK(state IN('QUEUED','RUNNING','SUCCEEDED','FAILED','CANCELLED')),
 model TEXT, prompt_version TEXT, result_json TEXT CHECK(result_json IS NULL OR json_valid(result_json)),
 error_code TEXT, created_at_ms INTEGER NOT NULL, completed_at_ms INTEGER);
CREATE TABLE repair_external_exports(
 id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES repair_tasks(id), task_version INTEGER NOT NULL,
 correlation_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL CHECK(state IN('NOT_CONFIGURED','PENDING','SUCCEEDED','FAILED','UNKNOWN')),
 connector TEXT NOT NULL, external_id TEXT, receipt_json TEXT CHECK(receipt_json IS NULL OR json_valid(receipt_json)),
 created_at_ms INTEGER NOT NULL, updated_at_ms INTEGER NOT NULL,
 CHECK(state!='NOT_CONFIGURED' OR external_id IS NULL));
CREATE TABLE repair_auth_sessions(
 token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES repair_users(id), csrf_hash TEXT NOT NULL,
 expires_at_ms INTEGER NOT NULL, revoked_at_ms INTEGER);
CREATE TABLE repair_host_pairings(
 id TEXT PRIMARY KEY, app_id TEXT NOT NULL, app_digest TEXT NOT NULL, instance_id TEXT NOT NULL, display_name TEXT NOT NULL,
 user_code_hash TEXT NOT NULL, poll_secret_hash TEXT NOT NULL, approved_user_id TEXT REFERENCES repair_users(id),
 state TEXT NOT NULL CHECK(state IN('PENDING','APPROVED','ISSUED','EXPIRED')),
 created_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL);
CREATE TABLE repair_host_sessions(
 token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES repair_users(id), pairing_id TEXT NOT NULL UNIQUE REFERENCES repair_host_pairings(id),
 app_id TEXT NOT NULL, instance_id TEXT NOT NULL, expires_at_ms INTEGER NOT NULL, revoked_at_ms INTEGER);
