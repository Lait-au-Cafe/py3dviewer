# py3dviewer - A pretty simple python module to visualize 3D model data. 

## Installation

```
$ pip install -e git://github.com/Lait-au-Cafe/py3dviewer.git@master#egg=py3dviewer
```

## How to Use

A minimum code to display a simple square plane is like below. 

```Python
import py3dviewer


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
	model_vertices, 
	model_indices, 
	model_uvmap, 
	"img/texture_image.png", 
	"Simple Plane"
)

while True:
	if not viewer.update():
		print("Exit. ")
		break
```
