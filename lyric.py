import re


LINE_PATTERN = re.compile(r'(\[[^\[]*?\])')
TIMESTAMP_PATTERN = re.compile(r'^\[(\d+(:\d+){0,2}(\.\d+)?)\]$')
ATTR_PATTERN = re.compile(r'^\[([\w\d]+):(.*)\]$')


class AttrToken(object):
    """
    Represents tags with the form of ``[key:value]``
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return '{%s: %s}' % (self.key, self.value)


class StringToken(object):
    """
    Represents a line of lyric text
    """

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return '"%s"\n' % self.text


class TimeToken(object):
    """
    Represents tags with the form of ``[h:m:s.ms]``

    The time attribute is the timestamp in milliseconds
    """

    def __init__(self, string):

        parts = string.split('.')

        self.time = parts[0]

    def __repr__(self):
        return '[%s]' % self.time


def tokenize(content):
    """ Split the content of LRC file into tokens

    Returns a list of tokens
    
    Arguments:
    - `content`: UTF8 string, the content to be tokenized
    """

    def parse_tag(tag):
        m = TIMESTAMP_PATTERN.match(tag)
        if m:
            return TimeToken(m.group(1))
        m = ATTR_PATTERN.match(tag)
        if m:
            return AttrToken(m.group(1), m.group(2))
        return None

    def tokenize_line(line):
        pos = 0
        tokens = []
        while pos < len(line) and line[pos] == '[':
            has_tag = False
            m = LINE_PATTERN.search(line, pos)
            if m and m.start() == pos:
                tag = m.group()
                token = parse_tag(tag)
                if token:
                    tokens.append(token)
                    has_tag = True
                    pos = m.end()
            if not has_tag:
                break
        tokens.append(StringToken(line[pos:]))
        return tokens

    lines = content
    tokens = []
    for line in lines:
        tokens.extend(tokenize_line(line))
    return tokens


def parse_lrc(content):
    """
    Parse an lrc file

    Arguments:
    - `content`: LRC file content encoded in UTF8

    Return values: attr, lyrics
    - `attr`: A dict represents attributes in LRC file
    - `lyrics`: A list of dict with 3 keys: id, timestamp and text.
      The list is sorted in ascending order by timestamp. Id increases from 0.
    """
    tokens = tokenize(content)
    attrs = {}
    lyrics = []
    timetags = []
    for token in tokens:
        if isinstance(token, AttrToken):
            attrs[token.key] = token.value
        elif isinstance(token, TimeToken):
            timetags.append(token.time)
        else:
            for timestamp in timetags:
                lyrics.append({'timestamp': timestamp,
                               'text': token.text})
            timetags = []
    lyrics.sort(key=lambda a: a['timestamp'])
    i = 0
    for lyric in lyrics:
        lyric['id'] = i
        i = i + 1
    return attrs, lyrics
