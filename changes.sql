SELECT
  editions.id,
  editions.details <> LAG(editions.details, 1)
  OVER (
    PARTITION BY editions.document_id
    ORDER BY editions.updated_at
  ) AS changed_details,
  editions.details
FROM editions
INNER JOIN documents ON documents.id = editions.document_id
WHERE TRUE
  AND editions.state <> 'draft'
  AND left(editions.document_type, 11) <> 'placeholder'
  AND documents.locale = 'en'
;
