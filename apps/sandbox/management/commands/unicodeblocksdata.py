import collections

from django.core.management.base import BaseCommand, CommandError

URL = 'https://www.unicode.org/Public/UNIDATA/Blocks.txt'

UnicodeBlock = collections.namedtuple('UnicodeBlock', ('name', 'start_code', 'end_code'))

def from_hex_string(x):
    return int(x, 16)

def parse_block(string):
    string, name = string.rsplit('; ', 1)
    start_code, end_code = map(from_hex_string, string.split('..'))
    return UnicodeBlock(name, start_code, end_code)

def retrieve_unicode_blocks():

    import requests

    r = requests.get(URL, stream=True)
    r.raise_for_status()

    blocks = []

    for line in map(lambda s: s.strip(), r.iter_lines(decode_unicode=True)):

        if line == '' or line.startswith('#'):
            continue

        try:
            block = parse_block(line)
        except (TypeError, ValueError) as error:
            raise error
        else:
            blocks.append(block)

    return sorted(blocks, key=lambda b: b.name)


class Command(BaseCommand):
    help = 'Retrieve data on unicode blocks with labels and ranges'

    def handle(self, *args, **options):
        import json

        unicode_blocks = retrieve_unicode_blocks()

        json_data = json.dumps({
            # FIXME: translate labels at some point
            'labels': [block.name for block in unicode_blocks],
            'ranges': [[block.start_code, block.end_code] for block in unicode_blocks]
        })

        self.stdout.write(json_data)

