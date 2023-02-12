#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2023 Denis Meyer
#
# This file is part of the monopoly probabilities application.
#

"""Monopoly Probabilities - MonopolyMain"""

import os
import os.path
import sys
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.colors as clrs
from tkinter import font
from PIL import Image, ImageTk
import pylab as pl
import numpy as np

from data.constants import COLORS
from data.constants import FONTS
from data.constants import SIZES
from data.translations import Translations
from threads.game import Game

class MonopolyGUI(tk.Frame):
    """Main application GUI"""

    def __init__(self,
                 curr_workdir=os.getcwd(),
                 update_every_n_rounds=100000,
                 sleep_after_round=0,
                 mapinterval=[0, 1],
                 colormap=plt.get_cmap('coolwarm'),
                 debug=False):
        tk.Frame.__init__(self)
        self.curr_workdir = curr_workdir
        self.translations = Translations()
        self.mapinterval = mapinterval
        self.game = Game(callback_resumed=self.callback_resumed,
                         callback_paused=self.callback_paused,
                         callback_afterround=self.callback_afterround,
                         afterround_n_rounds=update_every_n_rounds,
                         afterround_sleep=sleep_after_round,
                         mapinterval=self.mapinterval,
                         debug=debug)
        self.colormap = colormap
        self.displaycolormap = self._create_colormap()

    def _create_colormap(self):
        """Creates and saves a colormap"""
        path = self.curr_workdir + '/assets/img/colorbar.png'
        # Yep, one huge try-catch-block... nothing important here
        try:
            a = np.array([[0,1]])
            pl.figure(figsize=(9, 1.5))
            pl.imshow(a, cmap=self.colormap)
            pl.gca().set_visible(False)
            cax = pl.axes([0, 0.25, 0.75, 1])
            pl.colorbar(orientation='horizontal', cax=cax)
            pl.savefig(path)
            print('Successfully written colormap to {}'.format(path))
            return True
        except Exception as e:
            print('Failed to write colormap to {}'.format(path), e)
            return False

    def display(self):
        """Initializes the GUI and starts the main loop"""
        self._initgui()
        self.game.start()
        self.mainloop()

    def _center(self):
        """Centers the window"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        frm_width = self.master.winfo_rootx() - self.master.winfo_x()
        win_width = width + 2 * frm_width
        height = self.master.winfo_height()
        titlebar_height = self.master.winfo_rooty() - self.master.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.master.winfo_screenwidth() // 2 - win_width // 2
        y = self.master.winfo_screenheight() // 2 - win_height // 2
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.master.resizable(width=False, height=False)
        self.master.deiconify()

    def callback_resumed(self):
        """Callback when simulation resumed"""
        self._update_rounds_label()
        self._update_streetprobabilities()

    def callback_paused(self):
        """Callback when simulation paused"""
        self._update_rounds_label()
        self._update_streetprobabilities()

    def callback_afterround(self):
        """Callback after every n simulation rounds"""
        self._update_rounds_label()
        self._update_streetprobabilities()

    def _draw_board(self):
        """Draws the canvas"""
        imagepath = self.curr_workdir + '/assets/img/board.png'
        img = Image.open(imagepath)
        img = img.resize((self.imgsize, self.imgsize), Image.ANTIALIAS)
        self.img_board = ImageTk.PhotoImage(img)
        self.canvas.create_image(self.imgsize / 2 + self.pad,
                                 self.imgsize / 2 + self.pad,
                                 anchor=tk.CENTER,
                                 image=self.img_board)
        if self.displaycolormap:
            self.canvas_problabel = self.canvas.create_text(self.imgsize / 2 + self.pad - 232,
                                                            self.imgsize / 2 + 185,
                                                            anchor=tk.CENTER,
                                                            text=self.translations.get('GUI.LABELS.PROBABILITYCMAP'),
                                                            font=self.font_probcmaplabel)
            imagepath = self.curr_workdir + '/assets/img/colorbar.png'
            img = Image.open(imagepath)
            img = img.resize((400, 75), Image.ANTIALIAS)
            self.img_cmap = ImageTk.PhotoImage(img)
            self.canvas.create_image(self.imgsize / 2 + self.pad - 100,
                                     self.imgsize / 2 + self.pad + 200,
                                     anchor=tk.CENTER,
                                     image=self.img_cmap)
        self.canvas_statuslabel = self.canvas.create_text(self.imgsize / 2 + self.pad + 100,
                                                          self.imgsize / 2 + self.pad - self.font_processingstatus_def['size'] - 250,
                                                          anchor=tk.CENTER,
                                                          text=self.translations.get('GUI.LABELS.STATUS'),
                                                          font=self.font_processinglabel)
        self.canvas_status = self.canvas.create_text(self.imgsize / 2 + self.pad + 100,
                                                     self.imgsize / 2 + self.pad - 250,
                                                     anchor=tk.CENTER,
                                                     text=self.translations.get('GUI.ACTIONS.CLICKTOSTART'),
                                                     font=self.font_processingstatus)
        self.canvas_rounds = self.canvas.create_text(self.imgsize / 2 + self.pad + 100,
                                                     self.imgsize / 2 + self.pad + self.font_processingstatus_def['size'] - 250,
                                                     anchor=tk.CENTER,
                                                     text='',
                                                     font=self.font_roundslabel)

    def _draw_rects(self):
        """Draws the rectangles"""
        # Rect around board image
        self.rect_outer = self.canvas.create_rectangle(5,
                                                       5,
                                                       self.canvassize,
                                                       self.canvassize,
                                                       width=2,
                                                       outline=COLORS['rect_outer'],
                                                       fill='')
        # Rect around board image
        self.rect_board = self.canvas.create_rectangle(self.pad,
                                                       self.pad,
                                                       self.imgsize + self.pad,
                                                       self.imgsize + self.pad,
                                                       width=2,
                                                       outline=COLORS['rect_board'],
                                                       fill='')

    def _draw_streetseparators(self):
        """Draws the street separators"""
        # Frames to separate streets
        # Streets North
        streets_n_start = [157, 6, 157, 40]
        streets_n_plus = 76
        streets_n_no = range(10)
        for street_no in streets_n_no:
            self.canvas.create_line(streets_n_start[0] + street_no * streets_n_plus,
                                    streets_n_start[1],
                                    streets_n_start[2] + street_no * streets_n_plus,
                                    streets_n_start[3],
                                    fill=COLORS['streets_n'],
                                    width=3)
        # Streets East
        streets_e_start = [961, 157, 999, 157]
        streets_e_plus = 76
        streets_e_no = range(10)
        for street_no in streets_e_no:
            self.canvas.create_line(streets_e_start[0],
                                    streets_e_start[1] + street_no * streets_e_plus,
                                    streets_e_start[2],
                                    streets_e_start[3] + street_no * streets_e_plus,
                                    fill=COLORS['streets_e'],
                                    width=3)
        # Streets South
        streets_s_start = [157, 961, 157, 999]
        streets_s_plus = 76
        streets_s_no = range(10)
        for street_no in streets_s_no:
            self.canvas.create_line(streets_s_start[0] + street_no * streets_s_plus,
                                    streets_s_start[1],
                                    streets_s_start[2] + street_no * streets_s_plus,
                                    streets_s_start[3],
                                    fill=COLORS['streets_s'],
                                    width=3)
        streets_w_start = [6, 157, 40, 157]
        streets_w_plus = 76
        streets_w_no = range(10)
        for street_no in streets_w_no:
            self.canvas.create_line(streets_w_start[0],
                                    streets_w_start[1] + street_no * streets_w_plus,
                                    streets_w_start[2],
                                    streets_w_start[3] + street_no * streets_w_plus,
                                    fill=COLORS['streets_w'],
                                    width=3)

    def _update_streetprobabilities(self):
        """Updates the street probabilities"""
        str_label_prob = self.translations.get('GUI.LABELS.PROB')
        # Probabilities South
        for index, sb in enumerate(self.probs_s):
            prob = self.game.getprobability(index)
            prob_mapped = self.game.mapprobability(index)
            self.canvas.itemconfig(sb,
                                   text=str_label_prob.format(prob * 100),
                                   fill=clrs.to_hex(self.colormap(prob_mapped)))
        # Probabilities West
        for index, sb in enumerate(self.probs_w):
            prob = self.game.getprobability(index + 10)
            prob_mapped = self.game.mapprobability(index + 10)
            self.canvas.itemconfig(sb,
                                   text=str_label_prob.format(prob * 100),
                                   fill=clrs.to_hex(self.colormap(prob_mapped)))
        # Probabilities North
        for index, sb in enumerate(self.probs_n):
            prob = self.game.getprobability(index + 20)
            prob_mapped = self.game.mapprobability(index + 20)
            self.canvas.itemconfig(sb,
                                   text=str_label_prob.format(prob * 100),
                                   fill=clrs.to_hex(self.colormap(prob_mapped)))
        # Probabilities East
        for index, sb in enumerate(self.probs_e):
            prob = self.game.getprobability(index + 30)
            prob_mapped = self.game.mapprobability(index + 30)
            self.canvas.itemconfig(sb,
                                   text=str_label_prob.format(prob * 100),
                                   fill=clrs.to_hex(self.colormap(prob_mapped)))

    def _draw_streetprobabilities(self):
        """Draws the street probabilities"""
        # Probabilities South
        self.probs_s = []
        probs_s_start = [880, 980]
        probs_s_plus = 76
        probs_s_no = range(10)
        for probs_no in probs_s_no:
            self.probs_s.append(self.canvas.create_text(probs_s_start[0] - probs_no * probs_s_plus,
                                                        probs_s_start[1],
                                                        anchor=tk.CENTER,
                                                        text='',
                                                        font=self.font_probslabel))
        # Probabilities West
        self.probs_w = []
        probs_w_start = [24, 880]
        probs_w_plus = 76
        probs_w_no = range(10)
        for probs_no in probs_w_no:
            self.probs_w.append(self.canvas.create_text(probs_w_start[0],
                                                        probs_w_start[1] - probs_no * probs_w_plus,
                                                        anchor=tk.CENTER,
                                                        angle=270,
                                                        text='',
                                                        font=self.font_probslabel))
        # Probabilities North
        self.probs_n = []
        probs_n_start = [120, 24]
        probs_n_plus = 76
        probs_n_no = range(10)
        for probs_no in probs_n_no:
            self.probs_n.append(self.canvas.create_text(probs_n_start[0] + probs_no * probs_n_plus,
                                                        probs_n_start[1],
                                                        anchor=tk.CENTER,
                                                        text='',
                                                        font=self.font_probslabel))
        # Probabilities East
        self.probs_e = []
        probs_e_start = [980, 120]
        probs_e_plus = 76
        probs_e_no = range(10)
        for probs_no in probs_e_no:
            self.probs_e.append(self.canvas.create_text(probs_e_start[0],
                                                        probs_e_start[1] + probs_no * probs_e_plus,
                                                        anchor=tk.CENTER,
                                                        angle=90,
                                                        text='',
                                                        font=self.font_probslabel))

    def _draw_frame(self):
        """Draws the board frames"""
        self._draw_rects()
        self._draw_streetseparators()
        self._draw_streetprobabilities()
        self._update_streetprobabilities()

    def _update_rounds_label(self):
        """Updates the rounds text"""
        self.canvas.itemconfig(self.canvas_rounds,
                               text=self.translations.get('GUI.LABELS.ROUNDS').format(self.game.nrofrolls))

    def _update_processing_text(self, processing=False):
        """Updates the processing text"""
        tr = self.translations.get('GUI.ACTIONS.PROCESSING' if processing else 'GUI.ACTIONS.PAUSING')
        self.canvas.itemconfig(self.canvas_status, text=tr)

    def _button_mouse1_released(self, event):
        """On mouse button 1 released"""
        self.processing = not self.processing
        self._update_processing_text(self.processing)
        if self.processing:
            self.game.resume()
        else:
            self.game.pause()
        # Translate mouse screen x, y coordinates to canvas coordinates
        #mousex = self.canvas.canvasx(event.x)
        #mousey = self.canvas.canvasy(event.y)
        #print('_button_mouse1_released: (x: {x}, y: {y})'.format(x=mousex, y=mousey))

    def _create_canvasbinding(self):
        """Binds actions to the canvas"""
        self.canvas.bind('<ButtonRelease-1>', self._button_mouse1_released)

    def _create_canvas(self):
        """Creates the canvas to draw on"""
        self.canvas = tk.Canvas(width=self.canvassize,
                                height=self.canvassize,
                                bg=COLORS['canvas_bg'])
        self.canvas.grid(row=0,
                         column=0,
                         sticky=tk.N+tk.E+tk.S+tk.W)
        self.canvas.grid(row=0, column=0)

    def _doquit(self):
        """Destroys the window and quits"""
        self.quit()
        self.destroy()
        sys.exit(0)

    def _registercommands(self):
        """Registers some commands on special events, e.g. 'exit'"""
        self.master.createcommand('exit', self._doquit)
        self.master.protocol('WM_DELETE_WINDOW', self._doquit)

    def _configureproperties(self):
        """Configures frame properties"""
        self.master.title(self.windowtitle)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.grid(sticky=tk.N+tk.E+tk.S+tk.W, padx=0, pady=0)

    def _create_variables(self):
        """Creates class variables"""
        self.processing = False
        self.windowtitle = self.translations.get('GUI.WINDOW.TITLE')
        self.font_processinglabel_def = FONTS['statuslabel']
        self.font_processinglabel = font.Font(family=self.font_processinglabel_def['family'],
                                              size=self.font_processinglabel_def['size'],
                                              weight=self.font_processinglabel_def['weight'])
        self.font_processingstatus_def = FONTS['status']
        self.font_processingstatus = font.Font(family=self.font_processingstatus_def['family'],
                                               size=self.font_processingstatus_def['size'],
                                               weight=self.font_processingstatus_def['weight'])
        self.font_roundslabel_def = FONTS['roundslabel']
        self.font_roundslabel = font.Font(family=self.font_roundslabel_def['family'],
                                          size=self.font_roundslabel_def['size'],
                                          weight=self.font_roundslabel_def['weight'])
        self.font_probslabel_def = FONTS['probslabel']
        self.font_probslabel = font.Font(family=self.font_probslabel_def['family'],
                                         size=self.font_probslabel_def['size'],
                                         weight=self.font_probslabel_def['weight'])
        self.font_probcmaplabel_def = FONTS['probcmaplabel']
        self.font_probcmaplabel = font.Font(family=self.font_probcmaplabel_def['family'],
                                            size=self.font_probcmaplabel_def['size'],
                                            weight=self.font_probcmaplabel_def['weight'])
        self.canvassize = SIZES['canvas']
        self.imgsize = SIZES['img_board']
        self.pad = (self.canvassize - self.imgsize) / 2

    def _initgui(self):
        """Initializes the GUI"""
        self._create_variables()
        self._configureproperties()
        self._registercommands()
        self._create_canvas()
        self._create_canvasbinding()
        self._draw_board()
        self._draw_frame()
        self._center()
