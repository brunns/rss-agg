#!/usr/bin/env python3

import asyncio

import yarl

from rss_agg.read_and_aggregate import read_and_generate_rss


def main():
    rss = asyncio.run(read_and_generate_rss(base_url=yarl.URL("https://www.theguardian.com")))
    print(rss)


if __name__ == "__main__":
    main()
