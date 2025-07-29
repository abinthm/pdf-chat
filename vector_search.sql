-- Enable the vector extension if not already enabled
create extension if not exists vector;

-- Create the function for vector search
create or replace function match_embeddings(
    query_embedding vector(384),
    match_pdf_id uuid,
    match_count int default 3
)
returns table(
    id uuid,
    pdf_id uuid,
    page_number int,
    text text,
    embedding vector(384),
    similarity float
) language plpgsql as $$
begin
    return query
    select
        e.id,
        e.pdf_id,
        e.page_number,
        e.text,
        e.embedding,
        1 - (e.embedding <#> query_embedding) as similarity
    from embeddings e
    where e.pdf_id = match_pdf_id
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$$; 