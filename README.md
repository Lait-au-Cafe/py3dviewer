# py3dviewer - A pretty simple python module to visualize 3D model data. 

## Installation

```
$ pip install -e git://github.com/Lait-au-Cafe/py3dviewer.git@master#egg=py3dviewer
```

## How to Use

A minimum code to display a simple square plane is like below. 

```Python
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

    viewer = py3dviewer.Viewer(
		"Test Simple", 		// The name of window
		model_vertices, 	// The vertex buffer of model
		model_indices, 		// The index buffer of model
		model_uvmap, 		// The uv map of model
		"img/invader.png")	// The path to the texture file

    while True:
        if not viewer.update():
            print("Exit. ")
            break
```
