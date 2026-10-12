-- Optional provenance; existing manually entered tasks retain NULL sources.
ALTER TABLE adapttrail_private.project_tasks
 ADD COLUMN source_assessment_id BIGINT REFERENCES adapttrail_private.assessments(id) ON DELETE SET NULL,
 ADD COLUMN source_check_index INTEGER CHECK(source_check_index >= 0);
CREATE UNIQUE INDEX tasks_assessment_check ON adapttrail_private.project_tasks(project_id,source_assessment_id,source_check_index);
CREATE INDEX tasks_source_assessment ON adapttrail_private.project_tasks(source_assessment_id);
-- Existing backend-only grants and RLS policy remain in effect.
