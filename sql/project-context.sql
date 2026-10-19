-- Additive migration; existing project ownership, grants and RLS remain in force.
ALTER TABLE adapttrail_private.drafts
    ADD COLUMN farm_context TEXT NOT NULL DEFAULT '{}';
