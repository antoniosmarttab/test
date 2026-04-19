import requests
import json
import time
import os
from datetime import datetime, timezone, timedelta

# ============================================================
# TWITTER CREDENTIALS
# ============================================================
AUTH_TOKEN = "81889435ad85cd0d789d2db87cf1da65393a70f8"
CT0 = "62b92db5253b03814e50bbb3ff73a3eb31cefd7928038f6f420bfdace9ca62f03c59d3e8f2a76a0d734e034a4b4a3fd37bb922e30a3aa820fe2baca99f787de33066c1dc0a27bd562f2386bb2dae8fc9"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

# ============================================================
# TELEGRAM CONFIG
# ============================================================
BOT_TOKEN = "8668559641:AAHAe-XIkJeNi3y6-DErOVjTacetoMZsG5M"
CHANNEL_ID = "@modamer247"

# ============================================================
# LEBANON TIMEZONE (UTC+3)
# ============================================================
BEIRUT_TZ = timezone(timedelta(hours=3))

# ============================================================
# SLEEP SETTINGS
# ============================================================
SLEEP_BETWEEN_ACCOUNTS = 7
SLEEP_BETWEEN_MESSAGES  = 2
INTERVAL_MINUTES        = 30

# ============================================================
# FALLBACK LAST IDS — used only if json file doesn't exist
# ============================================================
LAST_IDS_DEFAULT = {
    "MarioNawfal":    "2045971700152439015",
    "realDonaldTrump":"2027651077865157033",
    "Megatron_ron":   "2045971114682356077",
    "Tasnimnews_EN":  "2045848242986869012",
    "waqa2e3":        "2045968439177556034",
    "MTVLebanonNews": "2045973765356474419",
    "ALJADEEDNEWS":   "2045972948985557415",
    "lebanondebate":  "2045955832936911199",
    "France24_ar":    "2045951382641938882",
    "TuckerCarlson":  "2043645373911273597",
    "AP":             "2045925454167548330",
    "Iran":           "2045955248372547858",
    "AJENews":        "2045973472547877258",
    "RTarabic":       "2045974719719940350",
    "clashreport":    "2045976754121060789",
    "BRICSinfo":      "2045973716970992028",
    "BBCBreaking":    "2045914578454745125",
}

# ============================================================
# ALL ACCOUNTS
# ============================================================
ACCOUNTS = [
    {"user_id": "1319287761048723458", "screen_name": "MarioNawfal"},
    {"user_id": "25073877",            "screen_name": "realDonaldTrump"},
    {"user_id": "1225234593789423616", "screen_name": "Megatron_ron"},
    {"user_id": "1699037857",          "screen_name": "Tasnimnews_EN"},
    {"user_id": "1501536111398641665", "screen_name": "waqa2e3"},
    {"user_id": "397199380",           "screen_name": "MTVLebanonNews"},
    {"user_id": "144105935",           "screen_name": "ALJADEEDNEWS"},
    {"user_id": "169196848",           "screen_name": "lebanondebate"},
    {"user_id": "25049177",            "screen_name": "France24_ar"},
    {"user_id": "22703645",            "screen_name": "TuckerCarlson"},
    {"user_id": "51241574",            "screen_name": "AP"},
    {"user_id": "2180371",             "screen_name": "Iran"},
    {"user_id": "18424289",            "screen_name": "AJENews"},
    {"user_id": "71516564",            "screen_name": "RTarabic"},
    {"user_id": "3247652319",          "screen_name": "clashreport"},
    {"user_id": "1449140157903482882", "screen_name": "BRICSinfo"},
    {"user_id": "5402612",             "screen_name": "BBCBreaking"},
]

# ============================================================
# LAST ID FILE
# ============================================================
LAST_ID_FILE = "last_tweet_id.json"

def load_last_ids():
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, "r") as f:
            return json.load(f)
    # fallback to hardcoded defaults
    return dict(LAST_IDS_DEFAULT)

def save_last_ids(last_ids):
    with open(LAST_ID_FILE, "w") as f:
        json.dump(last_ids, f, indent=2)

# ============================================================
# TWITTER
# ============================================================
def build_headers(screen_name):
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "x-csrf-token": CT0,
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
        "Referer": f"https://x.com/{screen_name}",
        "Cookie": f"auth_token={AUTH_TOKEN}; ct0={CT0}; lang=en",
    }

def fetch_tweets(account):
    user_id     = account["user_id"]
    screen_name = account["screen_name"]
    variables = {
        "userId": user_id,
        "count": 20,
        "includePromotedContent": False,
        "withVoice": True,
    }
    features = {
        "rweb_cashtags_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
    }
    params = {
        "variables": json.dumps(variables),
        "features": json.dumps(features),
        "fieldToggles": json.dumps({"withArticlePlainText": False}),
    }
    url = "https://x.com/i/api/graphql/6fWQaBPK51aGyC_VC7t9GQ/UserTweets"
    response = requests.get(url, headers=build_headers(screen_name), params=params, timeout=15)
    response.raise_for_status()
    return response.json()

def parse_tweets(data, screen_name):
    tweets = []
    instructions = (
        data.get("data", {})
        .get("user", {})
        .get("result", {})
        .get("timeline", {})
        .get("timeline", {})
        .get("instructions", [])
    )
    for instruction in instructions:
        if instruction.get("type") == "TimelinePinEntry":
            continue
        for entry in instruction.get("entries", []):
            tweet = extract_tweet(entry, screen_name)
            if tweet:
                tweets.append(tweet)

    tweets.sort(key=lambda t: int(t["id"]))
    return tweets

def extract_tweet(entry, screen_name):
    try:
        item_content = entry.get("content", {}).get("itemContent", {})
        if item_content.get("itemType") != "TimelineTweet":
            return None

        result = item_content.get("tweet_results", {}).get("result", {})

        if result.get("__typename") == "TweetWithVisibilityResults":
            result = result.get("tweet", {})

        legacy = result.get("legacy", {})
        if not legacy:
            return None

        if legacy.get("full_text", "").startswith("RT @"):
            return None

        note_tweet = result.get("note_tweet", {})
        full_text = (
            note_tweet
            .get("note_tweet_results", {})
            .get("result", {})
            .get("text")
        ) or legacy.get("full_text", "")

        return {
            "id":          legacy.get("id_str"),
            "created_at":  legacy.get("created_at", ""),
            "text":        full_text,
            "screen_name": screen_name,
            "url": f"https://x.com/{screen_name}/status/{legacy.get('id_str')}",
        }
    except Exception:
        return None

# ============================================================
# TELEGRAM
# ============================================================
def send_to_telegram(tweet):
    text = tweet["text"]
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    try:
        dt_utc    = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        dt_beirut = dt_utc.replace(tzinfo=timezone.utc).astimezone(BEIRUT_TZ)
        date_str  = dt_beirut.strftime("%d %b %Y • %H:%M Lebanon")
    except Exception:
        date_str = tweet.get("created_at", "")

    message = (
        f"🐦 <b>@{tweet['screen_name']}</b>  |  <i>{date_str}</i>\n\n"
        f"{text}\n\n"
        f"🔗 <a href='{tweet['url']}'>View on X</a>"
    )
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=10,
    )
    return response.ok

# ============================================================
# MAIN JOB
# ============================================================
def job(last_ids):
    now = datetime.now(BEIRUT_TZ).strftime('%H:%M:%S')
    print(f"\n[{now} Lebanon] Checking {len(ACCOUNTS)} accounts...")

    for account in ACCOUNTS:
        screen_name = account["screen_name"]
        try:
            data   = fetch_tweets(account)
            tweets = parse_tweets(data, screen_name)

            if not tweets:
                print(f"  📭 @{screen_name}: no tweets found")
                time.sleep(SLEEP_BETWEEN_ACCOUNTS)
                continue

            last_sent_id = last_ids.get(screen_name, "0")

            new_tweets = [
                t for t in tweets
                if int(t["id"]) > int(last_sent_id)
            ]

            if not new_tweets:
                print(f"  📭 @{screen_name}: nothing new")
                time.sleep(SLEEP_BETWEEN_ACCOUNTS)
                continue

            for tweet in new_tweets:
                if send_to_telegram(tweet):
                    last_ids[screen_name] = tweet["id"]
                    print(f"  ✅ @{screen_name}: sent {tweet['id']}")
                time.sleep(SLEEP_BETWEEN_MESSAGES)

        except Exception as e:
            print(f"  ⚠️ @{screen_name}: {e}")

        time.sleep(SLEEP_BETWEEN_ACCOUNTS)

    save_last_ids(last_ids)
    now2 = datetime.now(BEIRUT_TZ).strftime('%H:%M:%S')
    print(f"  ✔ [{now2}] Done. Next run in {INTERVAL_MINUTES} min.")

# ============================================================
# START
# ============================================================
if __name__ == "__main__":
    print("🚀 Modamer 24/7 Bot started!")
    print(f"📋 {len(ACCOUNTS)} accounts | {INTERVAL_MINUTES} min interval | Lebanon time")

    last_ids = load_last_ids()
    print(f"📂 Loaded cursors for {len(last_ids)} accounts\n")

    job(last_ids)

    while True:
        time.sleep(INTERVAL_MINUTES * 60)
        job(last_ids)
