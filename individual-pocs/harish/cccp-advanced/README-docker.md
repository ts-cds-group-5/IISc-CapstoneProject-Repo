
```
-- print all the tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

select * from "product";


CREATE EXTENSION IF NOT EXISTS vector;

SELECT extname FROM pg_extension;

-- creating a vector table
CREATE TABLE vector_items (
  id SERIAL PRIMARY KEY,
  embedding vector(3)
);


select * from vector_items;


INSERT INTO vector_items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]'), ('[1,1,1]');


SELECT * FROM vector_items ORDER BY embedding <-> '[2,3,4]' LIMIT 1;

SELECT * FROM vector_items ORDER BY embedding <=> '[2,3,4]' LIMIT 1;
```
