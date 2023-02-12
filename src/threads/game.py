#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2023 Denis Meyer
#
# This file is part of the monopoly probabilities application.
#

"""Monopoly Probabilities - Game"""

import threading
import time
import random
from numpy import interp

from data.board import Board

class Game(threading.Thread):
    """The monopoly game"""

    def __init__(self,
                 callback_resumed=None,
                 callback_paused=None,
                 callback_afterround=None,
                 afterround_n_rounds=100000,
                 afterround_sleep=0,
                 mapinterval=[0, 1],
                 debug=False):
        threading.Thread.__init__(self)
        self.daemon = True # OK for main to exit even if instance is still running
        self.paused = True
        self.debug = debug
        self.state = threading.Condition()

        self.callback_resumed = callback_resumed
        self.callback_paused = callback_paused
        self.callback_afterround = callback_afterround
        self.afterround_n_rounds = afterround_n_rounds
        self.afterround_sleep = afterround_sleep
        self.mapinterval = mapinterval

        self.currposition = 0
        self.nrofrolls = 0
        self.board = Board()
        self.visits = [0 for i in range(self.board.nroffields)]

    def getprobability(self, fieldno):
        """Returns the probability of a specified field"""
        if fieldno < 0 or fieldno >= self.board.nroffields or self.nrofrolls <= 0:
            return 0
        return 0 if self.nrofrolls <= 0 else self.visits[fieldno] / self.nrofrolls

    def mapprobability(self, fieldno):
        """Returns the probability of a specified field"""
        if fieldno < 0 or fieldno >= self.board.nroffields or self.nrofrolls <= 0:
            return 0
        _min = min(self.visits)
        _max = max(self.visits)
        _f = self.visits[fieldno]
        return interp(_f, [_min, _max], self.mapinterval)

    def run(self):
        """Starts the thread"""
        while True:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified
            self.nrofrolls += 1
            diceroll1 = random.randint(0, 6)
            diceroll2 = random.randint(0, 6)
            self.currposition = (self.currposition + diceroll1 + diceroll2) % 40
            if self.debug:
                print('Dice 1: {}, Dice 2: {}, Current Position: {}'
                      .format(diceroll1, diceroll2, self.currposition))
            # Jump to jail if on special jail field
            if self.currposition == self.board.jailfield:
                if self.debug:
                    print('Going to jail')
                self.visits[self.currposition] += 1
                self.currposition = 10
            self.visits[self.currposition] += 1
            if (self.nrofrolls % self.afterround_n_rounds == 0) and self.callback_afterround:
                self.callback_afterround()
            if self.afterround_sleep > 0:
                time.sleep(self.afterround_sleep)

    def resume(self):
        """Resumes the thread"""
        with self.state:
            if self.callback_resumed:
                self.callback_resumed()
            self.paused = False
            self.state.notify() # unblock self if waiting

    def pause(self):
        """Pauses the thread"""
        with self.state:
            if self.callback_paused:
                self.callback_paused()
            self.paused = True # make self block and wait
