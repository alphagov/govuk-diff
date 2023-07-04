-- Queries to extract the govspeak or HTML content from documents of various
-- different schemas.

CREATE INDEX index_editions_on_schema_name ON editions (schema_name);

SELECT
  editions.id,
  details ->> 'body' AS content
FROM editions
WHERE
  schema_name IN (
    'calendar',
    'case_study',
    'consultation',
    'corporate_information_page',
    'detailed_guide',
    'document_collection',
    'fatality_notice',
    'history',
    'hmrc_manual_section',
    'html_publication',
    'news_article',
    'organisation',
    'publication',
    'service_manual_guide',
    'service_manual_service_standard',
    'speech',
    'statistical_data_set',
    'take_part',
    'topical_event_about_page',
    'working_group'
  )
;

SELECT
  editions.id,
  jsonb_path_query(details, '$.body[0].content') AS content
FROM editions
WHERE TRUE
  AND schema_name IN (
    'answer',
    'help_page',
    'manual',
    'manual_section',
    'person',
    'role',
    'simple_smart_answer',
    'specialist_document'
  )
 AND jsonb_path_query(details, '$.parts[0].body.content_type') = 'text/govspeak'
;

SELECT
  id,
  STRING_AGG(
    COALESCE(summary.summary, '') || content.content,
    chr(13) || chr(10)    -- CRLF
    || chr(13) || chr(10) -- CRLF
  ) AS content
FROM editions
  LEFT JOIN LATERAL (
    SELECT
      '##Summary'
        || chr(13) || chr(10) -- CRLF
        || chr(13) || chr(10) -- CRLF
        || (jsonb_path_query(details, '$.summary ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS summary
      ) AS summary on TRUE
  LEFT JOIN LATERAL (
    SELECT
      '##' || (jsonb_path_query(details, '$.parts[*]') ->> 'title')
        || chr(13) || chr(10) -- CRLF
        || chr(13) || chr(10) -- CRLF
        || (jsonb_path_query(details, '$.parts[*].body ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content')
       AS content
      ) AS content ON TRUE
WHERE TRUE
  AND schema_name IN (
    'guide',
    'travel_advice'
  )
GROUP BY id
;

SELECT
  id,
  base_path,
  ARRAY_TO_STRING(
    ARRAY[
       introduction.content,
       more_information.content,
       need_to_know.content
    ],
    chr(13) || chr(10)      -- CRLF
      || chr(13) || chr(10) -- CRLF
  ) AS content
FROM editions
LEFT JOIN LATERAL (
  SELECT
    '#Introduction'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.introduction ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS introduction ON TRUE
LEFT JOIN LATERAL (
  SELECT
    '#More information'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.more_information ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS more_information ON TRUE
LEFT JOIN LATERAL (
  SELECT
    '#Need to know'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.need_to_know ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS need_to_know ON TRUE
WHERE TRUE
  AND schema_name = 'place'
;

SELECT
  id,
  base_path,
  ARRAY_TO_STRING(
    ARRAY[
       introductory_paragraph.content,
       start_button_text.content,
       will_continue_on.content,
       more_information.content,
       what_you_need_to_know.content,
       other_ways_to_apply.content
    ],
    chr(13) || chr(10)      -- CRLF
      || chr(13) || chr(10) -- CRLF
  ) AS content
FROM editions
LEFT JOIN LATERAL (
  SELECT
    '#Introductory paragraph'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.introductory_paragraph ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS introductory_paragraph ON TRUE
LEFT JOIN LATERAL (
  SELECT
    '#Start button text'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || jsonb_path_query(details, '$ ? (exists (@.start_button_text)) .start_button_text') AS content
  ) AS start_button_text ON TRUE
LEFT JOIN LATERAL (
  SELECT
    '#More information'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.more_information ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS more_information ON TRUE
LEFT JOIN LATERAL (
  SELECT
    '#What you need to know'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.what_you_need_to_know ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS what_you_need_to_know ON TRUE
LEFT JOIN LATERAL (
  SELECT
    '#Will continue on'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.will_continue_on ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS will_continue_on ON TRUE
LEFT JOIN LATERAL (
  SELECT
    '#Other ways to apply'
      || chr(13) || chr(10) -- CRLF
      || chr(13) || chr(10) -- CRLF
      || (jsonb_path_query(details, '$.other_ways_to_apply ? (exists (@ ? (@.content_type == "text/govspeak")))') ->> 'content') AS content
  ) AS other_ways_to_apply ON TRUE
WHERE TRUE
  AND schema_name = 'transaction'
;
