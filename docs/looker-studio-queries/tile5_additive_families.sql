-- Tile 5: Top 5 Additive Families in Deceptive Products
-- Looker Studio Custom Query data source
-- Replace YOUR_PROJECT with your GCP project ID

WITH mapping AS (
  SELECT code, category FROM UNNEST([
    STRUCT('e100' AS code, 'Curcumin' AS category),
    STRUCT('e101', 'Riboflavin'),
    STRUCT('e150', 'Caramel Colors'),
    STRUCT('e160', 'Carotenes & Carotenoids'),
    STRUCT('e161', 'Carotenes & Carotenoids'),
    STRUCT('e162', 'Beetroot Red'),
    STRUCT('e163', 'Anthocyanins'),
    STRUCT('e200', 'Sorbates'), STRUCT('e202', 'Sorbates'), STRUCT('e203', 'Sorbates'),
    STRUCT('e210', 'Benzoates'), STRUCT('e211', 'Benzoates'),
    STRUCT('e212', 'Benzoates'), STRUCT('e213', 'Benzoates'),
    STRUCT('e220', 'Sulphites'), STRUCT('e221', 'Sulphites'), STRUCT('e222', 'Sulphites'),
    STRUCT('e223', 'Sulphites'), STRUCT('e224', 'Sulphites'), STRUCT('e226', 'Sulphites'),
    STRUCT('e227', 'Sulphites'), STRUCT('e228', 'Sulphites'),
    STRUCT('e249', 'Nitrites & Nitrates'), STRUCT('e250', 'Nitrites & Nitrates'),
    STRUCT('e251', 'Nitrites & Nitrates'), STRUCT('e252', 'Nitrites & Nitrates'),
    STRUCT('e300', 'Ascorbic Acid & Ascorbates'), STRUCT('e301', 'Ascorbic Acid & Ascorbates'),
    STRUCT('e302', 'Ascorbic Acid & Ascorbates'), STRUCT('e304', 'Ascorbic Acid & Ascorbates'),
    STRUCT('e306', 'Tocopherols'), STRUCT('e307', 'Tocopherols'),
    STRUCT('e308', 'Tocopherols'), STRUCT('e309', 'Tocopherols'),
    STRUCT('e260', 'Acetates'), STRUCT('e261', 'Acetates'),
    STRUCT('e262', 'Acetates'), STRUCT('e263', 'Acetates'),
    STRUCT('e270', 'Lactates'), STRUCT('e325', 'Lactates'),
    STRUCT('e326', 'Lactates'), STRUCT('e327', 'Lactates'),
    STRUCT('e330', 'Citric Acid & Citrates'), STRUCT('e331', 'Citric Acid & Citrates'),
    STRUCT('e332', 'Citric Acid & Citrates'), STRUCT('e333', 'Citric Acid & Citrates'),
    STRUCT('e334', 'Tartrates'), STRUCT('e335', 'Tartrates'),
    STRUCT('e336', 'Tartrates'), STRUCT('e337', 'Tartrates'),
    STRUCT('e338', 'Phosphates'), STRUCT('e339', 'Phosphates'), STRUCT('e340', 'Phosphates'),
    STRUCT('e341', 'Phosphates'), STRUCT('e343', 'Phosphates'),
    STRUCT('e450', 'Phosphates'), STRUCT('e451', 'Phosphates'), STRUCT('e452', 'Phosphates'),
    STRUCT('e322', 'Lecithins'),
    STRUCT('e400', 'Alginates'), STRUCT('e401', 'Alginates'), STRUCT('e402', 'Alginates'),
    STRUCT('e403', 'Alginates'), STRUCT('e404', 'Alginates'), STRUCT('e405', 'Alginates'),
    STRUCT('e406', 'Agar'),
    STRUCT('e407', 'Carrageenan'),
    STRUCT('e410', 'Gums'), STRUCT('e412', 'Gums'), STRUCT('e413', 'Gums'),
    STRUCT('e414', 'Gums'), STRUCT('e415', 'Gums'), STRUCT('e417', 'Gums'),
    STRUCT('e418', 'Gums'),
    STRUCT('e420', 'Polyols'), STRUCT('e421', 'Polyols'),
    STRUCT('e440', 'Pectins'),
    STRUCT('e460', 'Celluloses'), STRUCT('e461', 'Celluloses'), STRUCT('e463', 'Celluloses'),
    STRUCT('e464', 'Celluloses'), STRUCT('e465', 'Celluloses'), STRUCT('e466', 'Celluloses'),
    STRUCT('e471', 'Mono- & Diglycerides'), STRUCT('e472', 'Mono- & Diglycerides'),
    STRUCT('e500', 'Carbonates'), STRUCT('e501', 'Carbonates'),
    STRUCT('e503', 'Carbonates'), STRUCT('e504', 'Carbonates'),
    STRUCT('e551', 'Silicates'), STRUCT('e552', 'Silicates'),
    STRUCT('e553', 'Silicates'), STRUCT('e554', 'Silicates'),
    STRUCT('e620', 'Glutamates'), STRUCT('e621', 'Glutamates'), STRUCT('e622', 'Glutamates'),
    STRUCT('e623', 'Glutamates'), STRUCT('e624', 'Glutamates'), STRUCT('e625', 'Glutamates'),
    STRUCT('e950', 'Sweeteners'), STRUCT('e951', 'Sweeteners'), STRUCT('e952', 'Sweeteners'),
    STRUCT('e953', 'Sweeteners'), STRUCT('e954', 'Sweeteners'), STRUCT('e955', 'Sweeteners'),
    STRUCT('e960', 'Sweeteners'), STRUCT('e961', 'Sweeteners'), STRUCT('e962', 'Sweeteners'),
    STRUCT('e965', 'Polyols'), STRUCT('e966', 'Polyols'),
    STRUCT('e967', 'Polyols'), STRUCT('e968', 'Polyols'),
    STRUCT('e1400', 'Modified Starches'), STRUCT('e1401', 'Modified Starches'),
    STRUCT('e1402', 'Modified Starches'), STRUCT('e1403', 'Modified Starches'),
    STRUCT('e1404', 'Modified Starches'), STRUCT('e1410', 'Modified Starches'),
    STRUCT('e1412', 'Modified Starches'), STRUCT('e1413', 'Modified Starches'),
    STRUCT('e1414', 'Modified Starches'), STRUCT('e1420', 'Modified Starches'),
    STRUCT('e1422', 'Modified Starches'), STRUCT('e1440', 'Modified Starches'),
    STRUCT('e1442', 'Modified Starches'), STRUCT('e1450', 'Modified Starches'),
    STRUCT('e1451', 'Modified Starches')
  ])
),
exploded AS (
  SELECT
    REGEXP_EXTRACT(
      REPLACE(LOWER(tag), 'en:', ''),
      r'^(e\d+)'
    ) AS base_code
  FROM `YOUR_PROJECT.foodmythbuster.stg_products`,
    UNNEST(additives_tags) AS tag
  WHERE is_deceptive
),
joined AS (
  SELECT m.category, e.base_code
  FROM exploded e
  JOIN mapping m ON e.base_code = m.code
)
SELECT
  category,
  COUNT(*) AS occurrences,
  STRING_AGG(DISTINCT UPPER(base_code), '/' ORDER BY UPPER(base_code)) AS codes
FROM joined
GROUP BY category
ORDER BY occurrences DESC
LIMIT 5
