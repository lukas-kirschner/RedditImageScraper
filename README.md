# Reddit Image Downloader

A reddit application that downloads pictures and gifs from a given subreddit.

# Setup

1. Create a [reddit personal use script application](https://www.reddit.com/prefs/apps/).

2. Add a `credentials.json` file to the project root directory and add your application's credentials.
   ```json
   {
     "client_id": "ID",
     "client_secret": "SECRET",
     "password": "PASSWORD",
     "user_agent": "AGENT",
     "username": "USERNAME"
   }
   ```
3. Run `pip install -r requirements.txt`

# Usage

```
usage: Reddit Image Scraper [-h] -s SUBREDDIT [-l LIMIT] [-o DEST_DIR]

A Reddit Image Downloader that supports metadata scraping.

options:
  -h, --help            show this help message and exit
  -s SUBREDDIT, --subreddit SUBREDDIT
                        Specify the subreddit or user account to scrape. 
                        Valid formats include 
                           "https://www.reddit.com/r/wallpapers/",
                           "wallpapers",
                           "r/wallpapers",
                           "u/exampleuser", 
                           "reddit.com/user/exampleuser/submitted/?sort=top&t=day"
  -l LIMIT, --limit LIMIT
                        Specify the maximum number of new images to download
  -o DEST_DIR, --out-dir DEST_DIR
                        Specify the destination directory to download scraped files into. Default is "out/"
```

Your images will appear in the "images" folder created by the application.

__Helpful note:__ To view .gif files on a Mac select the image(s) and press `cmd` + `y`.


