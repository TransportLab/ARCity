# ARCity
Augmented reality city project. [See the live version here](https://transportlab.github.io/ARCity/?debug).

## Components
  1. Stereolabs zed camera controlled via a python script
  2. three.js scene rendered in chrome sent to a projector
  3. flask server to communicate between the components
  4. traffic assignment simulation

## Installation
  1. Download or clone this repository
  2. Install `python3` and make sure you have the packages `flask`, `jsonify` `flask_cors` `overpy` and `numpy` by running `pip install flask jsonify flask_cors overpy numpy`
  3. Open a terminal and `cd` to the directory you saved this repository
  4. In the terminal, run the local server with `FLASK_APP=app.py` then `flask run` OR if that doesn't work, try `python app.py`
  5. Open Google Chrome (or possibly Firefox, but untested)
  6. In Chrome, go to the following URL: `http://localhost:5000/src/index.html`


## Usage
Many system parameters are controlled by URL flags, which can be used as, e.g.:

```
http://localhost:5000/src/index.html?debug
```

which will put the system in debug mode.
