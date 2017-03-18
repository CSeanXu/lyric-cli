import os
import subprocess
import time
import asyncio
import click

from lyric import parse_lrc


class ShowLyric:

    def __init__(self):

        current_playing_info = self.get_current_playing()

        self.lyrics = self.get_local_lyric(current_playing_info)

        self.playing = current_playing_info.get('song_name')

        self._song_duration = current_playing_info.get('complete_ratio')[0]
        self._song_position = current_playing_info.get('complete_ratio')[1]

        self.timer_time = self._build_timer(self._song_position)

    @staticmethod
    def _build_timer(position):
        """
        Cast position to time format as those in the lyric file
        :param position: int
        :return:
        position: 15 ---> 00:15
        position: 65 ---> 01:05
        """
        minute_part = position // 60
        second_part = position % 60

        return '%s:%s' % (str(minute_part).zfill(2), str(second_part).zfill(2))

    @staticmethod
    def get_current_playing():

        command = ['cmus-remote', '-Q']

        p = subprocess.Popen(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        text = p.stdout.read()

        info = text.split('\n')

        complete_ratio = [int(info[2].split(' ')[1]), int(info[3].split(' ')[1])]

        file_full_dir = info[1][5:]

        file_dir = os.path.join('/', os.path.join('/', *file_full_dir.split('/')[:-1]))

        song_name = info[1].split('/')[-1].split('.')[0]

        return {
            'status': True,
            'path': file_dir,
            'song_name': song_name,
            'complete_ratio': complete_ratio
        }

    @staticmethod
    def get_local_lyric(current_playing_info):

        base_dir = os.path.join(current_playing_info.get('path'), 'lyric')

        lyric_name = current_playing_info.get('song_name') + '.lrc'

        lyric_full_path = os.path.join(base_dir, lyric_name)

        if os.path.exists(lyric_full_path):
            with open(lyric_full_path) as lyr:
                _, lyrics = parse_lrc(lyr)

            return lyrics

    def _check_status(self):
        """
        检查持是否切换歌曲
        检查当前播放进度
        :return:
        """

        status = self.get_current_playing()

        current_song = status.get('song_name')

        if current_song != self.playing:
            # 检查是否切换歌曲

            self.playing = current_song

            self.lyrics = self.get_local_lyric(status)

        self._song_duration = status.get('complete_ratio')[0]
        self._song_position = status.get('complete_ratio')[1]

        self.timer_time = self._build_timer(self._song_position)

    def _show_progress_bar(self):

        with click.progressbar(length=self._song_duration, label='Now Playing 《%s》:' % self.playing,
                               show_eta=False, fill_char='>', empty_char='-', color='green') as bar:
            bar.update(self._song_position)

    @asyncio.coroutine
    def show_lyric(self):

        tmp = []

        while True:

            for i, l in enumerate(self.lyrics):

                lyric_ts = l.get('timestamp')

                if lyric_ts == self.timer_time:

                    current_lyric = l.get('text')

                    self._show_progress_bar()
                    click.echo()
                    click.echo()

                    for played_lyrics in tmp[-5:]:
                        click.secho(played_lyrics, fg='green')

                    click.secho(current_lyric, fg='red')

                    for pending_lyrics in self.lyrics[i + 1:i + 5]:
                        click.secho(pending_lyrics.get('text'), fg='green')

                    click.clear()

                    tmp.append(l.get('text'))

                    self.lyrics.remove(l)

                continue

            self._check_status()

            time.sleep(0.5)


if __name__ == '__main__':
    sl = ShowLyric()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sl.show_lyric())
    loop.close()
