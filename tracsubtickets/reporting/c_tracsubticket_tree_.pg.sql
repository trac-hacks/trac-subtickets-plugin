-- Copyright (C) 2016 Theodor Norup
-- All rights reserved.

-- Redistribution and use in source and binary forms, with or without
-- modification, are permitted provided that the following conditions
-- are met:

-- 1. Redistributions of source code must retain the above copyright
--    notice, this list of conditions and the following disclaimer.
-- 2. Redistributions in binary form must reproduce the above copyright
--    notice, this list of conditions and the following disclaimer in
--    the documentation and/or other materials provided with the
--    distribution.
-- 3. The name of the author may not be used to endorse or promote
--    products derived from this software without specific prior
--    written permission.

-- THIS SOFTWARE IS PROVIDED BY THE AUTHOR `AS IS'' AND ANY EXPRESS
-- OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
-- WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
-- ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
-- DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
-- DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
-- GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
-- INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
-- WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
-- NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
-- SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

-- Auxiliary stored procedure for use with reporting of Trac subticket
-- hierarchies:

-- Return depth-first traversal of the subticket hiearachy.

-- Uses Common Table Expression; see
-- https://www.postgresql.org/docs/9.1/static/queries-with.html
-- for explanation of the technique

CREATE OR REPLACE FUNCTION tracsubticket_tree () RETURNS TABLE (id int, parent int, level int, path int[])

AS $$
WITH RECURSIVE tree AS (
     SELECT p.id,  
     	    s1.parent, 
	    1 AS level, 
	    array[id] AS path
     FROM ticket p
     	  FULL OUTER JOIN subtickets s1 ON p.id = s1.child
     WHERE s1.parent IS NULL
UNION ALL
     SELECT ch.id, 
     	    s2.parent, 
	    tr.level+1, 
	    path||ch.id
     FROM ticket ch INNER JOIN subtickets s2 ON ch.id = s2.child
     JOIN tree tr ON s2.parent = tr.id
)
SELECT id, parent, level, path
FROM tree
$$
LANGUAGE SQL;
