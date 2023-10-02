import time
import telebot
from apify_client import ApifyClient

# Constants
telegram_token = '6456477412:AAGzN1OhSAz5qpiEpZfdKIG1Q7hxTIhaXro'
APIFY_TOKEN = 'apify_api_AI5IBDg0J0GoH41zT0dJfUJkKal5KM3fh2PL'
telegram_bot = telebot.TeleBot(telegram_token)
client = ApifyClient(APIFY_TOKEN)
"""USERNAMES OF THE TWITTER ACCOUNTS"""
USERNAMES = [
    "watcherguru", "shibaarchives", "binance", "crypto_bitlord7", "certik", "coinmarketcap",
    "coingecko", "bull_bnb", "cryptoskullx", "ericcryptoman", "cryptocevo", "cryptocom",
    "bsc_daily", "BSCNews", "WhaleStatsBSC", "unusual_whales", "chinapumpWXC", "whalechart",
    "trustwallet", "okx", "kucoincom", "crypto", "cryptocom", "gate_io", "ElonMusk",
    "bitboy_crypto", "BitcoinMagazine", "TheMoonCarl", "cryptocapo_", "cryptomanran", "cryptotony__"
]  # List of usernames as you provided
group_last_tweet_urls = {}  # Will store last tweeted URL per group

def get_most_recent_tweet_url_from_apify(username):
    run_input = {
        "handles": [username],
        "tweetsDesired": 1  # Get the most recent 5 tweets
    }

    run = client.actor("VsTreSuczsXhhRIqa").call(run_input=run_input)
    items = client.dataset(run["defaultDatasetId"]).iterate_items()

    for item in items:
        if isinstance(item, dict) and 'url' in item:
            return item['url']
#this handles the start command
@telegram_bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        markup = telebot.types.InlineKeyboardMarkup()
        add_btn = telebot.types.InlineKeyboardButton("Add to Group", url=f"https://t.me/{telegram_bot.get_me().username}?startgroup=a")
        markup.add(add_btn)

        welcome_message = (
            "Welcome to our bot! We’re making it easy for everyone to raid the latest tweets!\n\n"
            "- Completely free for everyone to use\n\n"
            "- Fast and easy\n\n"
            "To get the most out of this bot, write out a shill message & pin it in your telegram group for your community to use during the raids!"
        )
        telegram_bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


    elif message.chat.type in ['group', 'supergroup']:

        if message.chat.id not in group_last_tweet_urls:
            group_last_tweet_urls[message.chat.id] = {username: None for username in USERNAMES}

            print(f"Added group {message.chat.id} to tracking list.")  # Log the addition

        telegram_bot.reply_to(message, "I'm ready to notify this group of new tweets!")


def get_and_send_tweets_for_all_groups():
    print(f"Checking for new tweets... Groups being tracked: {len(group_last_tweet_urls)}")

    # This dictionary will store new tweets that need to be sent to each group
    tweets_to_send = {}

    # Fetch tweets for all usernames
    for username in USERNAMES:
        tweet_url = get_most_recent_tweet_url_from_apify(username)
        print(f"Received tweet URL for {username}: {tweet_url}")  # Log the fetched tweet URL

        # Check each group to see if this is a new tweet for them
        for group_id, user_tweet_mapping in group_last_tweet_urls.items():
            last_tweet = user_tweet_mapping.get(username)
            if tweet_url != last_tweet:
                if group_id not in tweets_to_send:
                    tweets_to_send[group_id] = {}
                tweets_to_send[group_id][username] = tweet_url

    # Now, send the tweets to each group
    for group_id, tweets in tweets_to_send.items():
        message = "🚀 New tweets alert! 🚀\n\n"
        message += " | ".join([f'<a href="{url}">{username}</a>' for username, url in tweets.items()])
        try:
            telegram_bot.send_message(group_id, message, parse_mode="HTML", disable_web_page_preview=True)
            print(f"Sent message to group {group_id}")  # Log successful sending

            # Update the last tweeted URL for this group.
            group_last_tweet_urls[group_id].update(tweets)
        except Exception as e:
            print(f"Failed to send message to group {group_id}. Reason: {e}")  # Log failure


def main():
    while True:
        get_and_send_tweets_for_all_groups()
        time.sleep(120)  # Wait for 1 minute.
if __name__ == '__main__':
    # Start two threads: One for bot polling, one for checking tweets.
    from threading import Thread

    Thread(target=telegram_bot.polling, kwargs={'none_stop': True}).start()
    main()
