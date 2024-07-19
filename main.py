import discord
import requests
import random
from discord.ext import commands
import os

latest_transaction = None

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Command: /pr0n
@bot.slash_command(name="pr0n", description="")
async def topg(ctx):
    print("Fetching data...")
    data = get_rand_data()
    if data:
        print("Data received.")
        urls = []
        subTitles = []

        # Collect URLs and subreddit titles
        for subreddit in data.get("data", {}).get("discoverSubreddits", {}).get("items", []):
            subreddit_title = subreddit.get("title", "No Title")
            for post in subreddit.get("children", {}).get("items", []):
                for media_source in post.get("mediaSources", []):
                    if media_source.get("width") == 1080:
                        urls.append(media_source.get("url"))
                        subTitles.append(subreddit_title)

        # Select a random URL and corresponding subreddit title
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

def get_rand_data():
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
    data = {
        "query": " query DiscoverSubredditsQuery( $filter: MediaFilter $limit: Int $iterator: String $hostsDown: [HostDisk] ) { discoverSubreddits( isNsfw: true filter: $filter limit: $limit iterator: $iterator ) { iterator items { __typename url title secondaryTitle description createdAt isNsfw subscribers isComplete itemCount videoCount pictureCount albumCount isFollowing children( limit: 2 iterator: null filter: null disabledHosts: $hostsDown ) { iterator items { __typename url title subredditTitle subredditUrl redditPath isNsfw albumUrl isFavorite mediaSources { url width height isOptimized } } } } } } ",
        "variables": {"limit": 20, "filter": None, "hostsDown": ["NANO", "PICO"]},
        "authorization": None
    }

    try:
        print("Sending API request...")
        response = requests.post(url, headers=headers, json=data, timeout=10)  # 10-second timeout
        print("API request sent.")
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None

@bot.event
async def on_ready():
    print(f"{bot.user} is connected and ready.")

# Run the bot using an environment variable for the token
bot_token = os.getenv("DISCORD_BOT_TOKEN")
if bot_token:
    bot.run(bot_token)
else:
    print("Error: DISCORD_BOT_TOKEN environment variable not set.")
