import requests
import json

url = "https://api.scrolller.com/api/v2/graphql"
headers = {
    "Authority": "api.scrolller.com",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Content-Type": "text/plain;charset=UTF-8",
    "Accept": "*/*",
    "Origin": "https://scrolller.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://scrolller.com/",
    "Accept-Language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7"
}

# GraphQL query
query = """
query DiscoverSubredditsQuery(
    $filter: MediaFilter,
    $limit: Int,
    $iterator: String,
    $hostsDown: [HostDisk]
) {
    discoverSubreddits(
        isNsfw: true,
        filter: $filter,
        limit: $limit,
        iterator: $iterator
    ) {
        iterator
        items {
            __typename
            url
            title
            secondaryTitle
            description
            createdAt
            isNsfw
            subscribers
            isComplete
            itemCount
            videoCount
            pictureCount
            albumCount
            isFollowing
            children(
                limit: 2,
                iterator: null,
                filter: null,
                disabledHosts: $hostsDown
            ) {
                iterator
                items {
                    __typename
                    url
                    title
                    subredditTitle
                    subredditUrl
                    redditPath
                    isNsfw
                    albumUrl
                    isFavorite
                    mediaSources {
                        url
                        width
                        height
                        isOptimized
                    }
                }
            }
        }
    }
}
"""

# Variables for the query
variables = {
    "limit": 2,
    "filter": None,
    "hostsDown": None, 
}

data = {
    "query": query,
    "variables": variables,
    "authorization": None
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=4))
