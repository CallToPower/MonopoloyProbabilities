#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2023 Denis Meyer
#
# This file is part of the monopoly probabilities application.
#

"""Monopoly Probabilities - Board"""

class Board:
    """The monopoly board data"""

    def __init__(self):
        self.specialfields = [0, 10, 20, 30]
        self.jailfield = 30
        self.nroffields = 40
