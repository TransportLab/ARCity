# ARCity
Augmented reality city project. [See the live version here](https://transportlab.github.io/ARCity/projector.html?debug). [The user-facing GUI can be found here](https://transportlab.github.io/ARCity/GUI.html)

## Components
  1. Stereolabs zed camera controlled via a python script
  2. three.js scene rendered in chrome sent to a projector
  3. flask server to communicate between the components
  4. traffic assignment simulation
  5. systemd services to start everything on boot (see`SETUP_INSTRUCTIONS.md`)

## Installation
  1. Download or clone this repository. Save it into `/opt/ARCity/`.
  2. Set up the zed camera SDK by following the instructions [here](https://www.stereolabs.com/developers/release/)
  3. Install `python3` and make sure you have the required packages by running `pip install -r requirements.txt`
  4. Follow instructions in `SETUP_INSTRUCTIONS.md` to set up the systemd services.
  5. Reboot the computer and everything should start automatically.
  

## Usage
Many system parameters are controlled by URL flags, which can be used as, e.g.:

```
http://localhost:5000/src/index.html?debug
```

which will put the system in debug mode.
