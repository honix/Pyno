# Pyno — *Python-based data-flow visual programming*
![Pyno](docs/screenshots/particles.png)

**So, what you can?**
- real-time interactive development
- no predefined nodes - you will code yours 
- use python as you like (any libs and tips)
- crash-less errors
- perpetuum mobile (~60 fps bacchanalia)

*Pyno is an experiment. Real-world scenarios is confusing.*

# How to use

[Check wiki for advanced tutorials!](https://github.com/honix/Pyno/wiki)

**Basics:**

There are only three elements:

| Element | Description | Key on keyboard to spawn |
|-|-|:-:|
| **node** | is a function | **N** |
| **node from file** | exact same as node but loads from file | **O** |
| **field** | is a object, value or lambda function | **F** |
| **subpatch** | is a link to pyno-file, allows you to control complexity of your patches | **S** |

Controls:
- Use right-mouse-button to panning
- Save and load pyno-file using bottom-right buttons (S-save, L-load)
- Move and select elements by mouse, selected elements can be deleted by **Delete** key
- Selected elements can be **ctrl-c** and **ctrl-v**
- Nodes has a code inside, edit code just by pressing on node and hover code editor
- Last, you want to transfer data from element to element, just press and hold on pin and drop connection to other pin

![Pyno](docs/screenshots/edit.png)

# How to run
Make sure you have **Python 3.4** or better on your computer.

To install pyno you must run ```pip install .``` from this directory.
Pyno's dependencies `pyglet` and `pyperclip` are going to be installed automatically.
In detail:
```
$ git clone https://github.com/honix/Pyno.git
$ cd Pyno
$ pip install .
```
alternatively as one-liner:
```
$ pip install git+https://github.com/honix/Pyno.git
```
Then run ```pyno``` in a console. The pip install step is optional and needed only to be able to run pyno from any working directory.

# How to modify

To develop/modify code, you can install Pyno in "developer mode" by running `pip install -e .` in the Pyno directory. 
This runs setup.py and installs a link to the `pyno` directory, as if it were normally installed.

To run the tests, you need `pytest`  installed. 
You run `pytest` in the root directory of the repository. 
It will discover the tests in the `tests` directory and run them on the installed package. 
You will see a couple of flashing windows when they get instantiated.

If you have (on Linux) `xvfb` and the pytest plugin `pytest-xvfb` installed, the tests should automatically be run on the virtual framebuffer, so no windows should become visible. 
If this for some reason does not work, invoking pytest via `xvfb-run pytest` should do the trick.
