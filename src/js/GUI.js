import * as CSS from "../css/main.css";
import * as GUI_CSS from "../css/gui.css";
import json_file from "../../params.json5";

import JSON5 from 'json5';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
// import { nelderMead } from './node_modules/fmin/src/nelderMead.js'
import * as ROADS from './roads';
import { manage_keypress } from './calibrate'
import * as MODELS from './models';
import {Lut} from "./Lut";

const urlParams = new URLSearchParams(window.location.search);
let p;

fetch("params.json5")
    .then(r => 
        r.text()
    )
    .then((data) => {
        p = JSON5.parse(data);
        init()
    });

function init() { }