# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import py3dviewer

if __name__ == "__main__":
    model_vertices = [
         10,  10, 0., 
        -10,  10, 0., 
         10, -10, 0., 
        -10, -10, 0.]

    model_indices = [
        0, 1, 2, 
        1, 2, 3]

    model_uvmap = [
        1.0, 1.0, 
        0.0, 1.0, 
        1.0, 0.0, 
        0.0, 0.0]

    viewer = py3dviewer.Viewer("Test Lazy Regist.", [], [], [], "img/invader.png")
    timer_start = datetime.now()
    while True:
        if not viewer.update():
            print("Exit. ")
            break

        if timer_start and ((datetime.now() - timer_start) > timedelta(seconds=5)):
            viewer.update_model(model_vertices, model_indices, model_uvmap)
            timer_start = None
