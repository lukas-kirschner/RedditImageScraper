# Reddit Image Downloader

A Reddit application that downloads pictures from a given subreddit, scraping and storing all metadata.

# Setup

1. Create a [reddit personal use script application](https://www.reddit.com/prefs/apps/).

2. Add a `credentials.json` file to the project root directory and add your application's credentials.
   ```json
   {
     "client_id": "ID",
     "client_secret": "SECRET",
     "user_agent": "AGENT"
   }
   ```
3. Run `pip install -r requirements.txt`

# Usage

Run the script by typing `python3 download_images.py <args>`.

```
usage: Reddit Image Scraper [-h] -s SUBREDDIT [-l LIMIT] [-o DEST_DIR] [-c CONFIG_FILE]

A Reddit Image Downloader that supports metadata scraping.

options:
  -h, --help            show this help message and exit
  -s SUBREDDIT, --subreddit SUBREDDIT
                        Specify the subreddit or user account to scrape. Valid formats include "https://www.reddit.com/r/wallpapers/", "wallpapers", "r/wallpapers", "u/exampleuser", "reddit.com/user/exampleuser/submitted/?sort=top&t=day"
  -l LIMIT, --limit LIMIT
                        Specify the maximum number of new images to download
  -o DEST_DIR, --out-dir DEST_DIR
                        Specify the destination directory to download scraped files into. Default is "out/"
  -c CONFIG_FILE, --config CONFIG_FILE
                        Specifies the config file to read the configuration from. Defaults to a global config file in the user's configuration directory.
```

Your images will appear in the "out" folder created by the application.
If the given config file does not exist, a default config file will be created.