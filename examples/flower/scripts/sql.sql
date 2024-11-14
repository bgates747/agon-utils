-- SQLite

-- select right_idx, count(*) as numrecs
-- from matched_indices
-- group by right_idx
-- having count(*) > 1
-- order by count(*) desc;

-- select *
-- from bbcbasic24ez_lst
-- where address<>'';

-- SELECT t1.*, t2.*
-- FROM (
--     SELECT t1.idx AS idx1, t1.address AS address1, t1.opcode AS opcode1, t1.instruction AS instruction1, t1.matching AS matching1 
--     FROM bbcbasic24 AS t1
-- ) AS t1
-- JOIN matched_indices AS t3 ON t1.idx1 = t3.left_idx
-- LEFT JOIN (
--     SELECT t2.idx AS idx2, t2.address AS address2, t2.opcode AS opcode2, t2.instruction AS instruction2, t2.matching AS matching2 
--     FROM bbcbasic24ez AS t2
-- ) AS t2 ON t3.right_idx = t2.idx2
-- ORDER BY t1.idx1;

-- SELECT t1.idx1, t2.idx2, t1.address1, t2.address2, t1.instruction1, t2.instruction2, t1.matching1,
--     t4.src_file, t4.srccode
-- FROM (
--     SELECT t1.idx AS idx1, t1.address AS address1, t1.opcode AS opcode1, t1.instruction AS instruction1, t1.matching AS matching1 
--     FROM bbcbasic24 AS t1
-- ) AS t1
-- FULL JOIN matched_indices AS t3 ON t1.idx1 = t3.left_idx
-- FULL JOIN (
--     SELECT t2.idx AS idx2, t2.address AS address2, t2.opcode AS opcode2, t2.instruction AS instruction2, t2.matching AS matching2 
--     FROM bbcbasic24ez AS t2
-- ) AS t2 ON t3.right_idx = t2.idx2
-- LEFT JOIN bbcbasic24ez_lst AS t4 ON t2.address2 = LOWER(t4.address);

SELECT t1.idx, t1.idx1, t1.idx2, t1.address1, t1.address2, t1.instruction1, t1.instruction2, t1.matching1, t2.src_file, t2.srccode
FROM final_table AS t1
LEFT JOIN bbcbasic24ez_lst AS t2 ON t1.address2 = LOWER(t2.address)
ORDER BY t1.idx;