# VOA-Special-English-Crawler
A crawler for VOA Special English news.

The crawler will automatically collect all articles in VOA Special English (https://learningenglish.voanews.com/) websites from 1959 (the start of the VOA SE program) to 2018/12/31. All the URLs pointing to articles will be stored in a JSON file.
The JSON file is organized as a list of dicts of lists, with each date (formatted as YYYY/MM/DD) has at least one article that day as key, a list of URLs referring to articles 

I use "article" instead of "news" to describe the website content URLs pointing to, because they cover several types of articles. 

To start the crawler, install it and make sure all its dependencies are installed as well; then run the software using the following command:

python3 crawler.py -i -o <output-path + XXX.json>
