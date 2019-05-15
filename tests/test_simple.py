# -*- coding: utf-8 -*-
import os
import sys
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

    viewer = py3dviewer.Viewer("Test Simple", model_vertices, model_indices, model_uvmap, "img/invader.png")
    while True:
        if not viewer.update():
            print("Exit. ")
            break
