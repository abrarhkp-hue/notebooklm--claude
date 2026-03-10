Implements feature request #171 - Export Notebook Metadata and Sources via Python API

## Changes

- Add `NotebookMetadata` dataclass with `id`, `title`, `created_at`, `updated_at`, `sources`
- Add `SourceSummary` dataclass with `id`, `title`, `url`, `kind`
- Add `notebooks.get_metadata()` method to retrieve structured notebook metadata
- Export new types from `__init__.py`

## Example usage

```python
metadata = await client.notebooks.get_metadata(notebook_id)
print(f"Notebook: {metadata.title}")
for source in metadata.sources:
    print(f"  - {source.title} ({source.kind.value})")
```

Closes #171
