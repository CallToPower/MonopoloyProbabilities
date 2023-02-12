#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2023 Denis Meyer
#
# This file is part of the monopoly probabilities application.
#

"""Monopoly Probabilities - MonopolyMain"""

class Translations:
    """The translations"""

    _translations = {
        'GUI.ACTIONS.CLICKTOSTART': 'Click to start simulating',
        'GUI.ACTIONS.PAUSING': 'Not simulating.',
        'GUI.ACTIONS.PROCESSING': 'Simulating...',
        'GUI.LABELS.STATUS': 'Status:',
        'GUI.LABELS.ROUNDS': 'Rounds: {:,}',
        'GUI.LABELS.PROB': '{:2.3f}%',
        'GUI.LABELS.PROBABILITYCMAP': 'Probability Colormap:',
        'GUI.WINDOW.TITLE': 'Monopoly Probabilities'
    }

    def get(self, key, default=''):
        """Returns the value for the given key or - if not found - a default value"""
        try:
            return self._translations[key]
        except KeyError as e:
            print('Returning default for key \'{}\': {}'.format(key, e))
            return default
