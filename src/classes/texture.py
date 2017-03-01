# -*- coding: utf8 -*-
"""Class that represents single textures and animations"""
from os import path, listdir
import math
from pygame import image, transform, Color
from classes.helper_types import Size

from .constants import *


class Texture(object):
    """"Class that represents the animation"""

    def __init__(self, t_path, delay=1, extension=".png", rotations=True):
        """
        Initialize the animation object, load all frames
        Animation can be a texture if <t_path> is a file
        :param t_path: string
        :param extension: string
        """
        self.delay = delay
        self.animation = False
        self.rotations = rotations

        self.frames = []
        self.frame_number = 0
        self.paused = False

        self.changes = 0

        self.animation = path.isdir(t_path)
        if self.animation:
            for frame_file in self.get_sorted_files(t_path, extension):
                self.frames.append(image.load(t_path + "/" + frame_file))
            if len(self.frames) == 0:
                self.frames.append(image.load(NO_TEXTURE_IMAGE))

            self.source_frames = self.frames
            self.frame = self.frames[self.frame_number]
        else:
            if path.exists(t_path):
                self.frame = image.load(t_path)
            else:
                self.frame = image.load(NO_TEXTURE_IMAGE)
            self.source_frame = self.frame

        rect = self.frame.get_rect()
        self.size = Size(rect.width, rect.height)
        self.cached_size = self.size

        self.angle = 0
        self.cached_angle = self.angle

    @staticmethod
    def get_sorted_files(folder, extension):
        """
        Get all files with <extension> order by number from <folder>
        :param folder: string
        :param extension: string
        """
        if path.exists(folder):
            # get all images from folder
            frames_files = [x for x in listdir(folder) if x.endswith(extension)]
            # sort frames by their number
            frames_files.sort(key=lambda y: int(path.splitext(y)[0]))
        else:
            frames_files = []

        return frames_files

    def rot_center(self, image, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = image.get_rect()
        rot_image = transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def update(self):
        """
        updates current frame
        """
        #if self.cached_size != self.size:
        #    self.frame = transform.scale(self.frame, (self.size.width, self.size.height))
        #    self.cached_size = self.size
        if self.cached_angle != self.angle:
            self.frame = transform.scale(
                self.rot_center(self.source_frame, self.angle),
                (self.size.width, self.size.height)
            )
            self.cached_angle = self.angle

    def next_frame(self):
        """
        switch to the next image (or to the first if current is last)
        """
        if not self.paused and self.animation:
            self.changes += 1
            if self.changes % self.delay == 0:
                self.frame_number += 1
                if self.frame_number == len(self.frames):
                    self.frame_number = 0

                if self.cached_size != self.size:
                    new_frames = []
                    for frame in self.frames:
                        frame = transform.scale(frame, (self.size.width, self.size.height))
                        new_frames.append(frame)
                    self.frames = new_frames
                    self.cached_size = self.size
                if (self.cached_angle != self.angle) and self.rotations:
                    new_frames = []
                    for frame in self.source_frames:
                        if self.angle == 180:
                            frame = transform.flip(frame, True, False)
                        else:
                            frame = transform.rotate(frame, self.angle)
                        frame = transform.scale(frame, (self.size.width, self.size.height))  # todo: optimize
                        new_frames.append(frame)
                    self.frames = new_frames
                    self.cached_angle = self.angle

                self.frame = self.frames[self.frame_number]
