CREATE DATABASE IF NOT EXISTS rag;

CREATE USER IF NOT EXISTS assistantRAG IDENTIFIED WITH plaintext_password BY 'safety_password';

GRANT ALL ON rag.* TO assistantRAG;

USE rag;

CREATE TABLE IF NOT EXISTS chunk (
    id UUID,
    emb Array(Float32),
    text String,
    paragraph_id UUID
) ENGINE = MergeTree() ORDER BY id;

CREATE TABLE IF NOT EXISTS paragraph (
    id UUID,
    name String,
    text String,
    num String,
    images Map(String, String) -- the image path | image text
)ENGINE = MergeTree() ORDER BY id;