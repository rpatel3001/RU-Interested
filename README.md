# RU-Interested
Got a long wait between classes? See if there's an interesting lecture going on near you! Filter by time, department, campus, and/or building.

## Obsolete
This project is no longer maintained or hosted anywhere. If forked, it likely won't work without some work as it relies on scraping and minor changes to the page format will break it.

## Build
1. git clone https://github.com/rpatel3001/RU-Interested.git
2. pip install -r requirements.txt
3. python scrape.py
4. gunicorn serve:app
5. go to localhost:8000 in a browser
