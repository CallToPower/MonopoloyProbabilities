#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2023 Denis Meyer
#
# This file is part of the monopoly probabilities application.
#

"""Monopoly Probabilities - Main"""

import os
import matplotlib
matplotlib.use('TkAgg') # fix macOS crash
from matplotlib.colors import LinearSegmentedColormap

from gui.gui import MonopolyGUI

from sys import platform as sys_pf

if __name__ == '__main__':
    cmap = LinearSegmentedColormap.from_list('', ['blue', 'red']) #['#a6bddb', '#f03b20']
    gui = MonopolyGUI(curr_workdir=os.getcwd(),
                      update_every_n_rounds=100000,
                      sleep_after_round=0,
                      mapinterval=[0, 10],
                      colormap=cmap, #plt.get_cmap('coolwarm'),
                      debug=False)
    gui.display()
