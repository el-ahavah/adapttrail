-- Preserve existing observations and retain the task wording at recording time.
ALTER TABLE adapttrail_private.progress_entries
 ADD COLUMN source_task_id BIGINT REFERENCES adapttrail_private.project_tasks(id) ON DELETE SET NULL,
 ADD COLUMN source_task_title TEXT NOT NULL DEFAULT '';
CREATE INDEX progress_source_task ON adapttrail_private.progress_entries(source_task_id,id);
