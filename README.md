# Cloaked AI + Marqo

This is an example of using Marqo AI together with IronCore Labs Cloaked AI to query over encrypted AI embeddings.

## Functionality

Indexes two encrypted documents into Marqo and queries them out. The documents, query, encrypted versions of each, and search results are all printed.

## Usage

Wait for the "welcome to marqo" message from `marqo-1` before running the python script.

```
docker compose up
pmd run cloaked-marqo.py
```

