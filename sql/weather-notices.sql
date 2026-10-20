-- Private per-project preferences and latest check; preserve existing grants and RLS.
ALTER TABLE adapttrail_private.drafts
    ADD COLUMN weather_watch TEXT NOT NULL DEFAULT '{}';
