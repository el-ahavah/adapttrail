CREATE TABLE adapttrail_private.adaptations (
 project_id BIGINT PRIMARY KEY REFERENCES adapttrail_private.drafts(id) ON DELETE CASCADE,
 publication_id BIGINT REFERENCES adapttrail_private.publications(id) ON DELETE SET NULL,
 source_title TEXT NOT NULL, changes TEXT NOT NULL, reason TEXT NOT NULL
);
CREATE INDEX adaptations_source ON adapttrail_private.adaptations(publication_id);
ALTER TABLE adapttrail_private.adaptations ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON adapttrail_private.adaptations FROM PUBLIC,anon,authenticated;
GRANT SELECT,INSERT,UPDATE,DELETE ON adapttrail_private.adaptations TO adapttrail_app;
CREATE POLICY backend_access ON adapttrail_private.adaptations FOR ALL TO adapttrail_app USING(true) WITH CHECK(true);
