## 1.0 Use-case
- stay on top of upcoming ML, sourced from a variety of places (linkedin, reddit etc.)
- tried a Zapier integration initially > no support for linkedin, limited reddit support, payment required after x calls
- quickly outpaced by ferocious tweet liking

## 2.0 Creating sourecs
- retrieve data for github liked repos, reddit liked posts, twitter liked tweets, linkedin liked posts
- straight forward for reddit, twitter, github > official APIs, create apps etc.
- github > application token, read access
- reddit > reddit application > user agent string formatting?
- twitter > straight forward generation of application keys/tokens

## 2.1 Notion
- notion > create integration, explicitly approve access on the page
- specifically format input > rich text?

## 3.0 Linkedin
- post retrieval not currently supported in official API
- reviewed linkedin_api > handles auth, session, fetching
- under the hood, linkedin_api uses voyager API, linkedin's official, internal API > locate to page (reations) > source > search for specific data structure > pipe back into voyager API
- linkedin_api allows you to retrieve/query against novel voyager resources
- So I inspected the react page elements, but couldn't find any voyager resources to do with reacts :(
- at this point, started to consider scraping

### 3.1 Selenium scraping
- functional code with headfull browser
- clunky, issues when trying to run headless
- try playwright instead? a little more modern, less imperative

### 3.2 Playwright scraping
- `playwright install` install browsers
- generally much faster > using chromium instead of selenium chrome?
- still having problems running headless.. hard to debug as well?

## 4.0 Storing posts
- store data within a notion database > where I do most of my planning etc.
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

## 5.0 Packaging
- container > GUI for headful runs > test if works
- cloud function?
- bundle a bunch of API keys > env vars initially, probably use docker secrets?

  ### Playwright
  - install chromium extensions, as well as an x-server to render the browser
  - tweak run command `xvfb-run -a python main.py`

  ### Pyperclip
  - relies on the host system clipboard, which is not present within

## 6.0 Classification?
- one-problem, being that I use all of these platforms in a variety of ways; reddit for music stuff, twitter for memes, linkedin to support colleagues etc.
- basically need to classify posts
- using Argilla, label data, create a cheap classifier

## TODO:
- filtering/modelling
- actual writing
- containerisation > cloud function?

## Docker misc
docker build . -t notion-hoover