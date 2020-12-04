#!/usr/bin/python3

from argparse import ArgumentParser
from requests import get
from bs4 import BeautifulSoup
from re import compile as regex, search, findall
from os import system, mkdir
from os.path import exists, join
from time import sleep

QUALITIES = (144, 240, 360, 480, 720, 1080)

class Scraper:

    def __init__(self, playlist_url):
        """ get content of playlist page and parse it """
        self.souper = BeautifulSoup(get(playlist_url).text, 'html.parser')

    def get_playlist_title(self):
        """ extract playlist title text """
        return self.souper.find('h2', attrs={'class': 'text fs-1-5 light-80 dark-10'}).string
    
    def get_playlist_items(self):
        """ extract all videos urls """
        videos = self.souper.find_all('li', attrs={'class': regex('playlist-item')})
        return [self.get_video_url(f"https://aparat.com{video.find('a')['href']}") for video in videos]

    def get_video_url(self, video):
        return findall(r'"contentUrl": "(.+)"', get(video).text)[0]

def download_playlist(args):
    scraper = Scraper(args.playlist_url)
    
    videos = scraper.get_playlist_items()
    if args.print:
        print('\n'.join(videos))
        exit()

    folder = scraper.get_playlist_title()
    if not exists(scraper.get_playlist_title()):
        mkdir(scraper.get_playlist_title())

    try:
        for index, video in enumerate(videos):
            system(f"wget {video} -O '{join(folder, str(index+1))}.mp4' -c")
            sleep(1)
    except KeyboardInterrupt:
        exit()

def main():
    parser = ArgumentParser(prog='aparat-wget',
        description='play list downloader for aparat.com',
        epilog='By Zaimfar <github.com/zaimfar/aparat-wget>')
    parser.add_argument('playlist_url', help="playlist page url")
    parser.add_argument('-p', '--print', help="just print urls do not download!", action='store_true')

    args = parser.parse_args()
    args.playlist_url = args.playlist_url.replace('www.', '')
    if search(r'^(http|https)://aparat.com/playlist/', args.playlist_url):
        download_playlist(args)
    else:
        print("Error: URL is not for a playlist.")

if __name__ == "__main__":
    main()
