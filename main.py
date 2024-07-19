import discord
from discord.ext import commands
import requests
import random
import os

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Common API URL and headers
API_URL = "https://api.scrolller.com/api/v2/graphql"
HEADERS = {
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

# GraphQL queries
DISCOVER_QUERY = """
query DiscoverSubredditsQuery($filter: MediaFilter, $limit: Int, $iterator: String, $hostsDown: [HostDisk]) {
    discoverSubreddits(isNsfw: true, filter: $filter, limit: $limit, iterator: $iterator) {
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
            children(limit: 2, iterator: null, filter: null, disabledHosts: $hostsDown) {
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

SUBREDDIT_QUERY = """
query SubredditQuery($url: String!, $filter: SubredditPostFilter, $iterator: String) {
    getSubreddit(url: $url) {
        children(limit: 50, iterator: $iterator, filter: $filter, disabledHosts: null) {
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

@bot.command(name="sync", description="Sync slash commands")
async def sync(ctx):
    if ctx.author.id == int(os.getenv("DISCORD_USER_ID")):
        await bot.sync_commands()
        await ctx.send("Commands synced!")
    else:
        await ctx.send("You don't have permission to use this command.")

def make_api_request(query, variables):
    data = {
        "query": query,
        "variables": variables,
        "authorization": None
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

@bot.slash_command(name="pr0n", description="Fetch random NSFW content")
async def pr0n(ctx):
    data = make_api_request(DISCOVER_QUERY, {"limit": 10, "filter": None, "hostsDown": ["NANO", "PICO"]})
    if data:
        urls = []
        subTitles = []

        for subreddit in data.get("data", {}).get("discoverSubreddits", {}).get("items", []):
            subreddit_title = subreddit.get("title", "No Title")
            for post in subreddit.get("children", {}).get("items", []):
                for media_source in post.get("mediaSources", []):
                    if media_source.get("width") == 1080:
                        urls.append(media_source.get("url"))
                        subTitles.append(subreddit_title)

        if urls:
            randIndex = random.randint(0, len(urls) - 1)
            urlToSend = urls[randIndex]
            subToSend = subTitles[randIndex]

            response_message = f"{urlToSend}\nSubreddit: `{subToSend}`"
            await ctx.respond(response_message)
        else:
            await ctx.respond("No suitable URLs found.")
    else:
        print("No data received.")
        await ctx.respond("No data received or an error occurred.")

@bot.slash_command(name="pr0n_video", description="Fetch video from a specific subreddit")
async def sub_video(ctx, subreddit: str):
    variables = {
        "limit": 10,
        "url": f"/r/{subreddit}",
        "filter": "VIDEO",
        "hostsDown": None
    }
    data = make_api_request(SUBREDDIT_QUERY, variables)
    if data and "data" in data and "getSubreddit" in data["data"]:
        subreddit_data = data["data"]["getSubreddit"]
        children = subreddit_data.get("children", {}).get("items", [])
        
        if children:
            post = random.choice(children)
            
            best_video = None
            max_width = 0
            for media_source in post.get("mediaSources", []):
                if media_source.get("isOptimized", False) and media_source.get("url", "").endswith((".mp4", ".webm")):
                    width = media_source.get("width", 0)
                    if width > max_width:
                        max_width = width
                        best_video = media_source

            if best_video:
                response_message = f"{best_video['url']}\nSubreddit: `{subreddit}`\nTitle: {post.get('title', 'No Title')}"
                await ctx.respond(response_message)
            else:
                await ctx.respond(f"No suitable video found in r/{subreddit}")
        else:
            await ctx.respond(f"No posts found in r/{subreddit}")
    else:
        await ctx.respond(f"Failed to fetch video data from r/{subreddit}")

@bot.slash_command(name="pr0n_image", description="Fetch picture from a specific subreddit")
async def sub_picture(ctx, subreddit: str):
    variables = {
        "limit": 10,
        "url": f"/r/{subreddit}",
        "filter": "PICTURE",
        "hostsDown": None
    }
    data = make_api_request(SUBREDDIT_QUERY, variables)
    if data and "data" in data and "getSubreddit" in data["data"]:
        subreddit_data = data["data"]["getSubreddit"]
        children = subreddit_data.get("children", {}).get("items", [])
        
        if children:
            post = random.choice(children)
            
            # Find the best quality, optimized image URL
            best_image = None
            max_width = 0
            for media_source in post.get("mediaSources", []):
                if media_source.get("isOptimized", False):
                    width = media_source.get("width", 0)
                    if width > max_width:
                        max_width = width
                        best_image = media_source

            if best_image:
                response_message = f"{best_image['url']}\nSubreddit: `{subreddit}`\nTitle: {post.get('title', 'No Title')}"
                await ctx.respond(response_message)
            else:
                await ctx.respond(f"No suitable image found in r/{subreddit}")
        else:
            await ctx.respond(f"No posts found in r/{subreddit}")
    else:
        await ctx.respond(f"Failed to fetch picture data from r/{subreddit}")

@bot.event
async def on_ready():
    print(f"{bot.user} is connected and ready.")

if __name__ == "__main__":
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if bot_token:
        bot.run(bot_token)
    else:
        print("Error: DISCORD_BOT_TOKEN environment variable not set.")
