import * as THREE from './node_modules/three/build/three.module.js';
import { LineMaterial } from './node_modules/three/examples/jsm/lines/LineMaterial.js';
import { OrbitControls } from './node_modules/three/examples/jsm/controls/OrbitControls.js';
// import { nelderMead } from './node_modules/fmin/src/nelderMead.js'
import * as ROADS from './roads.js';
import { manage_keypress } from './calibrate.js'
import * as MODELS from './models.js';

var W = 25/2. // half width in LEGO studs (x direction)
var H = 25/2. // half height in LEGO studs (y direction)
var road_width = 2/2 // width of roads in studs
var block_length = 4 // one block is 4 LEGO studs
var server_url = 'http://localhost:5000'

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );
camera.position.z = 2*W;

var light = new THREE.AmbientLight( 0xFFFFFF ); // white light
scene.add( light );

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );
var controls = new OrbitControls( camera, renderer.domElement );

var geometry = new THREE.PlaneGeometry( 2*W, 2*H,Math.floor(2*W*10),Math.floor(2*H*10));
var base_material = new THREE.MeshStandardMaterial( {color: 0xFFFFFF });//, side: THREE.DoubleSide} );
var base_plane = new THREE.Mesh( geometry, base_material );
scene.add( base_plane );
base_plane.position.z = -0.1;

var road_material = new THREE.MeshStandardMaterial( {color: 0x000000});//, side: THREE.DoubleSide} );

var line_material = new LineMaterial( {
    color: 0xFFFFFF,
    linewidth: 4, // in pixels??????
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
    ROADS.add_road_network(base_plane,links,road_width,road_material,line_material)
    // calibrate_camera();

    window.addEventListener( 'resize', onWindowResize, false );
    onWindowResize();
    window.addEventListener('keypress', function(e) { manage_keypress(camera,e) });

    // MODELS.add_model('blue-jeep/Jeep.gltf',[0,0,0],[Math.PI/2.,0,0],0.1,scene)
    MODELS.add_model('yellow-jeep/1385 Jeep.gltf',[0,2,0],[Math.PI/2.,0,0],0.02,scene)
}
var last = 0 ;
function animate(now) {
    requestAnimationFrame( animate );
    line_material.resolution.set( window.innerWidth, window.innerHeight ); // resolution of the viewport

    if(!last || now - last >= 3000) { // every 5 seconds
        last = now;
        // on new heights from server:
        // ROADS.update_displacement_map(base_material,server_url,W,H);

        console.log('hi')
    }

    renderer.render( scene, camera );
};

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
}

animate();
