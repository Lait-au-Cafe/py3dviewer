# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
import py3dviewer

if __name__ == "__main__":
    model_vertices = []
    radius = 100
    for j in range(-100, 100):
        for i in range(-100, 100):
            residual = radius ** 2 - (i**2 + j**2)
            if residual < 0:
                continue
            else:
                model_vertices.append(i)
                model_vertices.append(j)
                model_vertices.append(math.sqrt(residual))

    viewer = py3dviewer.Viewer("Test Draw Points", model_vertices, [], [], "img/invader.png")
    while True:
        if not viewer.update():
            print("Exit. ")
            break
