# -*- coding: utf-8 -*-

from datetime import datetime


class Timer(object):
    """ A timer to account the elapsed playing.
    """

    def __init__(self, accuracy=0):
        """
        
        Arguments:
        - `accuracy`:The accuracy of the time provided by players.
          If the difference between the time provided by players and the time of
          the timer is greater than accuracy, the time of the timer will be adjust to
          the time of the player.
        """
        self._accuracy = accuracy
        self._started = False
        self._time = 0
        self._begintime = None

    def play(self):
        """
        Starts the timer
        """
        if not self._started:
            self._started = True
            self._begintime = datetime.now()

    def pause(self):
        """
        Stops the timer
        """
        self._time = self.time
        self._begintime = None
        self._started = False

    def stop(self):
        """
        Stops the timer and sets the elapsed time to 0
        """
        self.pause()
        self._time = 0

    @property
    def time(self):
        now = datetime.now()
        if self._started:
            return self._time + int((now - self._begintime).total_seconds() * 1000)
        else:
            return self._time

    @time.setter
    def time(self, value):
        self.set_time(value)

    def set_time(self, value):
        """
        Adjust the time.

        If the time needs to be adjusted, return True.
        """
        time = self.time
        if abs(time - value) > self._accuracy:
            self._time = value
            self._begintime = datetime.now()
            return True
        return False
