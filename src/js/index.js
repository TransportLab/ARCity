import * as CSS from "../css/main.css";
import json_file from "../../params.json5";

import JSON5 from 'json5';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
// import { nelderMead } from './node_modules/fmin/src/nelderMead.js'
import * as ROADS from './roads.js';
import { manage_keypress } from './calibrate.js'
import * as MODELS from './models.js';

const urlParams = new URLSearchParams(window.location.search);
let p; // parameters to be loaded from json file
let clock, scene, camera, renderer
let line_material, road_material, base_material;
let t_prev = 0;
let sun, base_plane;
let cars = [];

fetch("params.json5")
    .then(r => 
        r.text()
    )
    .then((data) => {
        p = JSON5.parse(data);
        // console.log(p)
        init()
    });
// init();
// var srcMat = new THREE.MeshStandardMaterial( {
// 					emissive: 0x00ff00,
// 					emissiveIntensity: 1,
// 					color: 0x000000
// 				} );
// window.source = new THREE.Mesh( sunGeometry, srcMat );
// var endMat = new THREE.MeshStandardMaterial( {
// 					emissive: 0xff0000,
// 					emissiveIntensity: 1,
// 					color: 0x000000
// 				} );
// window.dest = new THREE.Mesh( sunGeometry, endMat );
// scene.add(window.source);
// scene.add(window.dest);
// window.source.position.x = 1;
// window.source.position.z = 1; window.dest.position.z =1;

function init() {
    console.log(p)
    p.projector_plane_distance_studs = p.projector_plane_distance_mm/p.mm_per_stud; // distance in mm

    clock = new THREE.Clock();
    scene = new THREE.Scene();
    // var camera = new THREE.PerspectiveCamera( 50, window.innerWidth/window.innerHeight, 0.1, 1000 ); // vertical FOV angle, aspect ratio, near, far
    var fov_vertical = 2*Math.atan(p.projector_aspect_ratio/p.projector_throw_ratio/2.)*(180/Math.PI); // approx 59 degrees for a 0.5 throw ratio
    camera = new THREE.PerspectiveCamera( fov_vertical, window.innerWidth/window.innerHeight, 0.1, 1000 ); // vertical FOV angle, aspect ratio, near, far


    // camera.rotation.x = -fov_vertical*Math.PI/180./2.; // half FOV angle - but then I need to rotate the plane back??
    // console.log(camera.rotation.x)
    // var ambient_light = new THREE.AmbientLight( 0xFFFFFF ); // white light
    // scene.add( ambient_light );
    var sunGeometry = new THREE.SphereGeometry( 0.1 ); // radius
    var sunMat = new THREE.MeshStandardMaterial( {
                        emissive: 0xffffee,
                        emissiveIntensity: 1,
                        color: 0x000000
                    } );
    sun = new THREE.PointLight( 0xFFFFFF, 1, 0, 2 ); // white light
    // sun.add( new THREE.Mesh( sunGeometry, sunMat ) );
    sun.castShadow = true;
    scene.add( sun );
    // sun.shadow.mapSize.width = 512*2;  // default
    // sun.shadow.mapSize.height = 512*2; // default
    sun.position.x = 0.5;
    sun.position.y = 0.5;
    sun.position.z = 1;

    renderer = new THREE.WebGLRenderer();
    renderer.shadowMap.enabled = true;
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    // renderer.gammaOutput = true;
    // renderer.gammaFactor = 2.2;
    document.body.appendChild( renderer.domElement );

    if ( urlParams.has('debug') ) {
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
    base_plane.receiveShadow = true;
    base_plane.castShadow = true;
    scene.add( base_plane );
    // base_plane.position.z = 0;//-0.01;

    road_material = new THREE.MeshStandardMaterial( {color: 0x000000});//, side: THREE.DoubleSide} );

    line_material = new LineMaterial( {
        color: 0xFFFFFF,
        linewidth: 2, // in pixels??????
        dashScale: 5,
        gapSize: 3,
        dashSize: 4
    } );
    line_material.defines.USE_DASH = ""; // enables dashing

    var links = ROADS.generate_regular_roads(p.W,p.H,p.road_width,p.block_length)
    var G = ROADS.generate_regular_roads_networkx(p.W,p.H,p.road_width,p.block_length)
    window.G = G;
    // locate_domain()
    
    scene.background = new THREE.Color( 0x000000 );
    ROADS.add_road_network(base_plane,links,p.road_width,road_material,line_material)
    // calibrate_camera();

    window.addEventListener( 'resize', onWindowResize, false );
    onWindowResize();
    window.addEventListener('keypress', function(e) { manage_keypress(camera,e) });
    //                file,                       rot,            scale,parent,G,link,cars,R
    
    function add_async_models() {
        return new Promise(async(resolve, reject) => {
            await MODELS.load_model('yellow-jeep/1385 Jeep.gltf',[Math.PI/2.,0,0],0.01,p.road_width);
            await MODELS.load_model('blue-jeep/Jeep.gltf',       [Math.PI/2.,0,0],0.05,p.road_width);
            // console.log('loaded car models')
            for (var i=0;i<p.num_cars;i=i+2) {
                MODELS.add_model(0,scene,G,i  ,cars);
                MODELS.add_model(1,scene,G,i+1,cars);
            }
            
        });
    }

    add_async_models();
    

    ROADS.update_traffic_randomly(G,2,3);

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
    }

    sun.position.x = 2*p.W*Math.sin(t*2.*Math.PI/p.sun_period);
    sun.position.z = 2*p.W*Math.cos(t*2.*Math.PI/p.sun_period);
    // console.log(sun.rotation)

    // var speed = 2; // vehicle speed
    cars.forEach( function(car, index) {
        if ( car.isturning ) {
            MODELS.turn_car(car,p.road_width);
        }
        else {
            var edge = G.getEdgeData(car.nodes[0],car.nodes[1]);
            ROADS.check_for_intersection(G,car,p.road_width)
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


