## 사용되는 카탈로그 조회 쿼리를 딕셔너리 형태로 관리.
catalog_quries = {
    'database_info' : """
        SELECT 
            current_database() as database,
            pg_catalog.shobj_description(d.oid, 'pg_database') as comment
        FROM pg_catalog.pg_database d
        WHERE datname = current_database();
    """,
    'schema_info' : """
        SELECT 
            schema_name,
            obj_description(n.oid, 'pg_namespace') as comment
        FROM information_schema.schemata s
        JOIN pg_namespace n ON n.nspname = s.schema_name
        WHERE schema_name in (select distinct schemaname as schema_name from pg_tables where schemaname not in ('information_schema','pg_catalog'))
    """,
    'table_info' : """
        select
            pt.table_schema as table_schema,
            pt.table_name as table_name,
            pt.table_type as table_type,
            obj_description(c.oid) as table_comment
        from information_schema.tables pt
        join pg_class c on c.relname = pt.table_name
        where pt.table_schema not in ('information_schema','pg_catalog') and pt.table_schema = :schema_name
    """,
    'column_info' : """
        with constraint_pk_table as (
            SELECT
                tc.table_schema,
                tc.table_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
        )
        SELECT 
            c.table_schema,
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            CASE 
                WHEN pk.column_name IS NOT NULL THEN 'YES'
                ELSE 'NO' 
            END as is_primary_key,
            col_description(pgc.oid, a.attnum) as column_comment
        FROM information_schema.columns as c
        left JOIN pg_class pgc ON pgc.relname = c.table_name
        left JOIN pg_attribute a ON a.attrelid = pgc.oid AND a.attname = c.column_name
        left join constraint_pk_table pk on c.column_name = pk.table_name
        WHERE c.table_schema NOT IN ('information_schema', 'pg_catalog') and c.table_name = :table_name
    """,
    'fk_info' : """
        SELECT
            tc.table_schema,
            tc.table_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
    """
}