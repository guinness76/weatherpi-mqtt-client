#!/usr/bin/python3

import math
from gpiozero import Button
from signal import pause
from time import sleep

# Argent Data Systems rain volume sensor

class RainVolume():
    def __init__(self):
        self.interval_secs=5
        self.drops = 0
        self.rainBucket = Button(6)
        self.rainBucket.when_pressed = self.onBucketDrop

    def onBucketDrop(self):
        self.drops = self.drops + 1
        # print("onBucketDrop fired")

    def getBucketDrops(self):
        return self.drops

    def resetBucketDrops(self):
        self.rotationCount = 0

bucket = RainVolume()

print("Waiting for 5 second rain bucket test: add water now")
#pause()

acc = 0
while acc<5:
    sleep(1)
    acc += 1

drops = bucket.getBucketDrops()
print("At the end of 5 seconds, %d bucket drop(s) recorded." % drops)
