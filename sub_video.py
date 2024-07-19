import requests
import json

url = "https://api.scrolller.com/api/v2/graphql"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://scrolller.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Priority": "u=4",
    "TE": "trailers"
}

# GraphQL query
query = """
query SubredditQuery(
    $url: String!,
    $filter: SubredditPostFilter,
    $iterator: String
) {
    getSubreddit(url: $url) {
        children(
            limit: 50,
            iterator: $iterator,
            filter: $filter,
            disabledHosts: null
        ) {
            iterator
            items {
                __typename
                id
                url
                title
                subredditId
                subredditTitle
                subredditUrl
                redditPath
                isNsfw
                albumUrl
                hasAudio
                fullLengthSource
                gfycatSource
                redgifsSource
                ownerAvatar
                username
                displayName
                isPaid
                tags
                isFavorite
                mediaSources {
                    url
                    width
                    height
                    isOptimized
                }
                blurredMediaSources {
                    url
                    width
                    height
                    isOptimized
                }
            }
        }
    }
}
"""

# Variables for the query
variables = {
    "limit": 2,
    "url": "/r/animals",
    "filter": "VIDEO",
    "hostsDown": None
}

data = {
    "query": query,
    "variables": variables,
    "authorization": None,
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=4))
