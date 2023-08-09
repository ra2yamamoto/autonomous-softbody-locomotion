In order to run the pretrained models, there are a few specific things you must install. I would recommend first following the installation instructions on the PyBox2D github and then installing the rest.

- PyBox2D, following the instructions on https://github.com/pybox2d/pybox2d.

- NEAT-Python. (Using `pip` should be sufficient)

- Pygame. (Again, `pip` is fine)

- Python, **must be version 3.8.10**.

With all these installed in a virtualenv, run any of the files containing "visual" in their name. For eaxmple, you might run `python recurrent visual trial 2.py ` in a terminal. If you wish to change which network the body uses (and in the case of `recurrent visual arbitrary body shape.py`, the body shape), feel free to change the paths specified in the code to other network models. All network data is stored in `nn data`.

The `tools` file is analogous to the code found at `https://github.com/ra2yama/softbody-tools`, and serves to run the testbed.

