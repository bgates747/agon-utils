-- Define the base CTEs for label definitions and references
WITH defs AS (
    SELECT label AS label_def, def_file
    FROM label_defs
), refs AS (
    SELECT DISTINCT label AS label_ref, ref_file
    FROM label_refs
),
find_refs(label, def_file, ref_file, level) AS (
    SELECT
        defs.label_def as label,
        defs.def_file,
        NULL AS ref_file,
        0 AS level
    FROM defs
    WHERE defs.def_file = 'tmp1.asm'

    -- UNION ALL

    -- SELECT
    --     refs.label_ref as label,
    --     defs.def_file,
    --     NULL AS ref_file,
    --     1 AS level
    -- FROM refs
    -- JOIN defs ON refs.label_ref = defs.label_def
    -- WHERE refs.ref_file = 'tmp1.asm'

    UNION ALL

    -- Recursive step: find labels referenced in the def_file of the current label
    SELECT
        refs.label_ref as label,
        defs.def_file,
        refs.ref_file,
        find_refs.level + 1
    FROM find_refs
    JOIN refs ON refs.ref_file = find_refs.def_file
    JOIN defs ON refs.label_ref = defs.label_def
    WHERE refs.ref_file <> 'tmp1.asm'  -- Exclude the initial file to prevent cycles
      AND find_refs.level < 10
)
SELECT
    substr('..........', 1, level * 3) || label AS label_hierarchy,
    def_file,
    ref_file
FROM find_refs
ORDER BY level;
