import re
import typer
import requests
import pandas as pd
from html import unescape
from datetime import datetime


def clean_title(title):
    if(re.search(r'&#.*;', title)):
        return unescape(title)
    return title


def clean_tags(tags):
    string_tags = ','.join([t for t in tags])
    if(re.search(r'&#.*;', string_tags)):
        return unescape(string_tags).split(',')
    return tags


def generate_entries(items):
    for item in items:
        tags = clean_tags(item['tags'])
        title = clean_title(item['title'])
        yield {
            'question_id': item['question_id'],
            'tags': tags,
            'title': title,
            'title_and_tags': f'{title}{", ".join([t for t in tags])}',
            'creation_timestamp': datetime.fromtimestamp(item['creation_date']).strftime("%Y-%m-%d %H:%M:%S"),
            'score': item['score'],
            'link': item['link']
        }


def request_questions(params, url, page_limit):
    r = requests.get(url, params=params)
    print(f'REQUESTED PAGE {params["page"]} OF URL: {r.url}')
    res = r.json()
    if(res['has_more'] and params['page'] < page_limit):
        params['page'] += 1
        yield from request_questions(params, url, page_limit)

    for entry in generate_entries(res['items']):
        yield entry


def assemble_dataframe(params, url, page_limit):
    df = pd.DataFrame()
    ct = 0
    for res in request_questions(params, url, page_limit):
        df = df.append(res, ignore_index=True)
        ct += 1
    return df, ct


def output_data(save_csv, site, ct, df, outfile):
    if(save_csv):
        if(len(outfile) == 0):
            outfile = f'{site}-{ct}-{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}'
        df.to_csv(f'./{outfile}.csv', sep=',')
    else:
        print(df)


def main(
    url: str = 'https://api.stackexchange.com/2.2/questions',
    page_limit: int = 2,
    save_csv: bool = False,
    outfile: str = '',
    starting_page: int = 1,
    page_size: int = 2,
    site: str = 'pt.stackoverflow'
):
    params = {
        'page': starting_page,
        'pagesize': str(page_size),
        'order': 'desc',
        'sort': 'activity',
        'site': site
    }
    df, ct = assemble_dataframe(params, url, page_limit)
    output_data(save_csv, site, ct, df, outfile)
    print(f'Done! Fetched {ct} entries!')


if(__name__ == '__main__'):
    typer.run(main)
