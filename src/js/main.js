import * as THREE from './node_modules/three/build/three.module.js';
import { LineMaterial } from './node_modules/three/examples/jsm/lines/LineMaterial.js';
import { OrbitControls } from './node_modules/three/examples/jsm/controls/OrbitControls.js';
// import { nelderMead } from './node_modules/fmin/src/nelderMead.js'
import * as ROADS from './roads.js';
import { manage_keypress } from './calibrate.js'

var W = 25/2. // half width in LEGO studs (x direction)
var H = 25/2. // half height in LEGO studs (y direction)
var road_width = 2/2 // width of roads in studs
var block_length = 4 // one block is 4 LEGO studs

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );
camera.position.z = 2*W;

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );
var controls = new OrbitControls( camera, renderer.domElement );

var geometry = new THREE.PlaneGeometry( 2*W, 2*H,2*W,2*H);
var base_material = new THREE.MeshBasicMaterial( {color: 0xffffff, side: THREE.DoubleSide} );
var base_plane = new THREE.Mesh( geometry, base_material );
scene.add( base_plane );
base_plane.position.z = -0.1;

var road_material = new THREE.MeshBasicMaterial( {color: 0x000000, side: THREE.DoubleSide} );

var line_material = new LineMaterial( {
    color: 0xFFFFFF,
    linewidth: 4, // in pixels??????
    // vertexColors: false,
    //resolution:  // to be set by renderer, eventually
    dashScale: 5,
    gapSize: 3,
    dashSize: 4
} );
line_material.defines.USE_DASH = ""; // enables dashing

var links = ROADS.generate_regular_roads(W,H,road_width,block_length)

// locate_domain()

scene.background = new THREE.Color( 0xFF0000 );
init();

function init() {
    ROADS.add_road_network(scene,links,road_width,road_material,line_material)
    // calibrate_camera();

    window.addEventListener( 'resize', onWindowResize, false );
    onWindowResize();
    window.addEventListener('keypress', function(e) { manage_keypress(camera,e) });
}

var animate = function () {
    requestAnimationFrame( animate );
    line_material.resolution.set( window.innerWidth, window.innerHeight ); // resolution of the viewport

    // on new heights from server:
    // ROADS.update_displacement_map();


    renderer.render( scene, camera );
};

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
}

animate();
