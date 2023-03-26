## Linkedin
- not currently supported in official API
- not currently supported with linkedin API
- scrape?

## Notion integration
- had to search for the database ID manually:
https://developers.notion.com/reference/post-search
https://www.reddit.com/r/Notion/comments/nembqc/database_id_not_found/
https://www.python-engineer.com/posts/notion-api-python/

```
curl -X POST 'https://api.notion.com/v1/search' \
  -H 'Authorization: Bearer '"<secret>"'' \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2022-06-28' \
  --data '{
    "query":"resarch",
    "filter": {
        "value": "database",
        "property": "object"
    },
    "sort":{
      "direction":"ascending",
      "timestamp":"last_edited_time"
    }
  }'
```

Getting these weird errors when I just use naive text:
    body.properties.text.files should be defined, instead was `undefined`.
    body.properties.text.status should be defined, instead was `undefined`.
    body.properties.text.id should be defined, instead was `undefined`.
    body.properties.text.name should be defined, instead was `undefined`.
    body.properties.text.start should be defined, instead was `undefined`.
- format as "rich_text" instead?
    "text": {"rich_text": [{"text": {"content": record['text']}}]},

## Classification?
- ML/not ML
- topic/usefulness
- using rubrix

## TODO:
- linkedin posts
- github libraries
- pocket articles/summaries