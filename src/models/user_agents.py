from random import randint


WINDOWS_VERSIONS = [
    '5.1',
    '6.1',
    '6.2',
    '6.3',
    '10.0'
]


CHROME_VERSIONS = [
    '124',
    '125',
    '126',
    '127',
    '128',
    '129',
    '130',
    '131'
]


USER_AGENTS = [
    f'Mozilla/5.0 (Windows NT {WINDOWS_VERSIONS[randint(0, len(WINDOWS_VERSIONS) - 1)]}; Win64; x64) '
    f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VERSIONS[randint(0, len(CHROME_VERSIONS) - 1)]}.0.0.0 '
    f'Safari/537.36',
    f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VERSIONS[randint(0, len(CHROME_VERSIONS) - 1)]}.0.0.0 Safari/537.36",
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VERSIONS[randint(0, len(CHROME_VERSIONS) - 1)]}.0.0.0 Safari/537.36"
]
