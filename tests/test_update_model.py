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

    model_uvmap = [
        1.0, 1.0, 
        0.0, 1.0, 
        1.0, 0.0, 
        0.0, 0.0]

    viewer = py3dviewer.Viewer(model_vertices, model_uvmap, "img/invader.png", "Sample")
    while True:
        if not viewer.update():
            print("Exit. ")
            break
        model_vertices = [v * 1.0002 for v in model_vertices]
        viewer.update_model(model_vertices, model_uvmap)
