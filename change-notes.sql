-- The latest change note per edition.
-- There shouldn't be more than one change-note per editon, yet there is for
-- some very old editions.
WITH
latest_change_note AS (
  SELECT DISTINCT ON (edition_id)
    edition_id,
    note
  FROM change_notes
  ORDER BY edition_id, updated_at
),
SELECT
  documents.content_id,
  editions.updated_at,
  editions.update_type,
  change_notes.note,
  editions.state,
  editions.phase,
  editions.content_store,
  editions.base_path,
  editions.document_type,
  editions.schema_name,
  editions.title,
  editions.description,
  editions.routes,
  editions.redirects,
  editions.details
FROM editions
INNER JOIN documents ON documents.id = editions.document_id
LEFT JOIN latest_change_note ON latest_change_note.edition_id = editions.id
WHERE TRUE
  AND editions.state <> 'draft'
  AND left(document_type, 11) <> 'placeholder'
  AND locale = `en`
