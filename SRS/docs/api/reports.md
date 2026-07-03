# Reports API

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/reports/pipeline-summary/` | Status totals and trends |
| `GET` | `/api/v1/reports/source-performance/` | Source conversion metrics |
| `GET` | `/api/v1/reports/interview-funnel/` | Interview progression metrics |
| `GET` | `/api/v1/reports/export/` | Export filtered data |

## Response Considerations

- report endpoints should support date filters
- expensive aggregations may require caching

