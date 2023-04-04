## Use-case
- stay on top of upcoming ML, sourced from a variety of places (linkedin, reddit etc.)
- tried a Zapier integration initially > no support for linkedin

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

## Linkedin
- linkedin_api > handles auth, session, fetching
- voyager API > locate to page (reations) > source > search for specific data structure > pipe back into voyager API
- nothing in these requests :( > nothing to do with reacts

## Selenium
- functional code with headfull browser
- clunky, issues when trying to run headless
- try playwright instead? a little more modern, less imperative

## Playwright
- `playwright install` install browsers
- generally much faster > using native chrome instead of selenium chrome?
- using chromium instead
- still having problems running headless.. hard to debug as well?

## Classification?
- ML/not ML
- topic/usefulness
- using rubrix

## TODO:
- linkedin posts
- github libraries
- pocket articles/summaries
- filtering/modelling
- reddit submission/post patchy data