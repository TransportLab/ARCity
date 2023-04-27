import * as CSS from "../css/main.css";
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
let p; // parameters to be loaded from json file
let clock, scene, camera, renderer
let line_material, road_material, base_material;
let t_prev = 0;
let sun, base_plane;
let cars = [];
let road_lut = new Lut('grayscale',512);

fetch("params.json5")
    .then(r => 
        r.text()
    )
    .then((data) => {
        p = JSON5.parse(data);
        init()
    });

function init() {
    p.projector_plane_distance_studs = p.projector_plane_distance_mm/p.mm_per_stud; // distance in mm

    clock = new THREE.Clock();
    scene = new THREE.Scene();

    var fov_vertical = 2*Math.atan(p.projector_aspect_ratio/p.projector_throw_ratio/2.)*(180/Math.PI); // approx 59 degrees for a 0.5 throw ratio
    camera = new THREE.PerspectiveCamera( fov_vertical, window.innerWidth/window.innerHeight, 0.1, 1000 ); // vertical FOV angle, aspect ratio, near, far

    var ambient_light = new THREE.AmbientLight( 0x555555 ); // white light
    scene.add( ambient_light );

    sun = new THREE.PointLight( 0xFFFFFF, 1, 0, 2 ); // white light
    sun.castShadow = true;
    scene.add( sun );

    if ( p.show_sun ) {
        var sunGeometry = new THREE.SphereGeometry( 0.1 ); // radius
        var sunMat = new THREE.MeshStandardMaterial( {
                            emissive: 0xffffee,
                            emissiveIntensity: 1,
                            color: 0x000000
                        } );
        sun.add( new THREE.Mesh( sunGeometry, sunMat ) );
    }

    sun.position.x = 0.5;
    sun.position.y = 0.5;
    sun.position.z = 1;

    renderer = new THREE.WebGLRenderer();
    renderer.shadowMap.enabled = true;
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );

    document.body.appendChild( renderer.domElement );

    if ( urlParams.has('debug') ) {
        console.log(p);
        camera.position.z = 30;
        var controls = new OrbitControls( camera, renderer.domElement );
    }
    else {
        camera.position.z = p.projector_plane_distance_studs;
        camera.position.y = -p.projector_plane_distance_studs/p.projector_throw_ratio/p.projector_aspect_ratio; // vertical offset
    }

    var geometry = new THREE.PlaneGeometry( 2*p.W, 2*p.H,Math.floor(2*p.W*10),Math.floor(2*p.H*10));
    base_material = new THREE.MeshStandardMaterial( {color: 0xFFFFFF, side: THREE.DoubleSide} );
    base_plane = new THREE.Mesh( geometry, base_material );
    base_plane.castShadow = true;
    scene.add( base_plane );

    road_material = new THREE.MeshStandardMaterial({
        color: 0x000000,
        opacity : 0.9,
        side: THREE.DoubleSide,
        transparent: true,
    });

    line_material = new LineMaterial( {
        color: 0xFFFFFF,
        linewidth: 4, // in pixels??????
        dashScale: 5,
        gapSize: 3,
        dashSize: 4
    } );
    line_material.defines.USE_DASH = ""; // enables dashing

    ROADS.generate_regular_roads_networkx(p.W,p.H,p.road_width,p.block_length,scene,road_material,line_material);
    
    scene.background = new THREE.Color( 0x000000 );

    window.addEventListener( 'resize', onWindowResize, false );
    onWindowResize();
    window.addEventListener('keypress', function(e) { manage_keypress(camera,e) });
    
    function add_async_models() {
        return new Promise(async(resolve, reject) => {
            await MODELS.load_model('yellow-jeep/1385 Jeep.gltf',[Math.PI/2.,0,0],0.01,p.road_width);
            await MODELS.load_model('blue-jeep/Jeep.gltf',       [Math.PI/2.,0,0],0.05,p.road_width);
            // console.log('loaded car models')
            for (var i=0;i<p.num_cars;i=i+2) {
                MODELS.add_model(0,scene,ROADS.G,i  ,cars);
                MODELS.add_model(1,scene,ROADS.G,i+1,cars);
            }
            
        });
    }

    add_async_models();
    ROADS.update_traffic_randomly(p.min_speed,p.max_speed,base_plane);
    animate();

}

function animate() {
    let dt = clock.getDelta(); 
    let t = clock.getElapsedTime();

    line_material.resolution.set( window.innerWidth, window.innerHeight ); // resolution of the viewport
    // console.log(t - t_prev)
    if(t - t_prev >= p.displacement_map_update_time) { // every 5 seconds
        t_prev = t;
        // on new heights from server:
        // ROADS.update_displacement_map(base_material,server_url,W,H);
        ROADS.fake_update_displacement_map(base_material,p.server_url,p.W,p.H);
        ROADS.update_traffic_randomly(p.min_speed,p.max_speed,base_plane);
    }

    sun.position.x = 2*p.W*Math.sin(t*2.*Math.PI/p.daily_period);
    sun.position.z = 2*p.W*Math.cos(t*2.*Math.PI/p.daily_period);
    // base_material.emissive = road_lut.getColor( 0.1 + 0.5*Math.abs(Math.sin(t*2.*Math.PI/p.daily_period)) );
    // road_material.emissiveIntensity = -Math.cos(t*2.*Math.PI/p.daily_period);
    // if ( road_material.emissiveIntensity < 0 ) { road_material.emissiveIntensity = 0;}
    // console.log(road_material.emissiveIntensity);
    // console.log(sun.rotation)

    // var speed = 2; // vehicle speed
    cars.forEach( function(car, index) {
        if ( car.isturning ) {
            MODELS.turn_car(car,p.road_width);
        }
        else {
            var edge = ROADS.G.getEdgeData(car.nodes[0],car.nodes[1]);
            ROADS.check_for_intersection(car,p.road_width)
            if      ( car.orientation === 'h' ) { car.position.x += car.direction*edge.speed*dt; }
            else if ( car.orientation === 'v' ) { car.position.y += car.direction*edge.speed*dt; }
            else { console.log('Orientation not defined. Not moving.'); }

        }
    });

    requestAnimationFrame( animate );
    renderer.render( scene, camera );
};

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
}


