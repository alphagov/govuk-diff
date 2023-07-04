CREATE OR REPLACE TABLE micropigs AS
SELECT
  editions.id,
  editions.updated_at,
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
  AND base_path = '/guidance/keeping-a-pet-pig-or-micropig'
;

\copy micropigs to './micropigs.csv';
