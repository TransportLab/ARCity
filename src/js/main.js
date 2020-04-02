import * as THREE from './node_modules/three/build/three.module.js';
import { LineMaterial } from './node_modules/three/examples/jsm/lines/LineMaterial.js';
import { OrbitControls } from './node_modules/three/examples/jsm/controls/OrbitControls.js';
// import { nelderMead } from './node_modules/fmin/src/nelderMead.js'
import * as ROADS from './roads.js';
import { manage_keypress } from './calibrate.js'
import * as MODELS from './models.js';

// LEGO BRICK DIMENSIONS //
// 8.0 mm - horizontal spacing from centre of one stud to another
// 9.6 mm - vertical height of regular brick
var mm_per_stud = 8.0; // JUST IN HORIZONTAL DIRECTION
var projector_throw_ratio = 0.5; // width of projected area / distance to
var projector_plane_distance_mm = 1000.0; // distance in mm
var projector_plane_distance_studs = projector_plane_distance_mm/mm_per_stud; // distance in mm


var W = 25/2. // half width in LEGO studs (x direction)
var H = 25/2. // half height in LEGO studs (y direction)
var road_width = 2/2 // width of roads in studs
var block_length = 4 // one block is 4 LEGO studs
var server_url = 'http://localhost:5000'

var clock = new THREE.Clock();
var scene = new THREE.Scene();
// var camera = new THREE.PerspectiveCamera( 50, window.innerWidth/window.innerHeight, 0.1, 1000 ); // vertical FOV angle, aspect ratio, near, far
var fov_vertical = 2*Math.atan(9./16.)*(180/Math.PI); // approx 59 degrees for a 0.5 throw ratio
console.log(fov_vertical)
var camera = new THREE.PerspectiveCamera( fov_vertical, window.innerWidth/window.innerHeight, 0.1, 1000 ); // vertical FOV angle, aspect ratio, near, far
camera.position.z = projector_plane_distance_studs;

// var ambient_light = new THREE.AmbientLight( 0xFFFFFF ); // white light
// scene.add( ambient_light );
var sunGeometry = new THREE.SphereBufferGeometry( 0.1 ); // radius
var sunMat = new THREE.MeshStandardMaterial( {
					emissive: 0xffffee,
					emissiveIntensity: 1,
					color: 0x000000
				} );
var sun = new THREE.PointLight( 0xFFFFFF, 1, 0, 2 ); // white light
sun.add( new THREE.Mesh( sunGeometry, sunMat ) );
sun.castShadow = true;
scene.add( sun );
// sun.shadow.mapSize.width = 512*2;  // default
// sun.shadow.mapSize.height = 512*2; // default
sun.position.x = 0.5;
sun.position.y = 0.5;
sun.position.z = 1;
console.log(sun.position)


var renderer = new THREE.WebGLRenderer();
renderer.shadowMap.enabled = true;
renderer.setPixelRatio( window.devicePixelRatio );
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );
var controls = new OrbitControls( camera, renderer.domElement );

var geometry = new THREE.PlaneGeometry( 2*W, 2*H,Math.floor(2*W*10),Math.floor(2*H*10));
var base_material = new THREE.MeshStandardMaterial( {color: 0xFFFFFF, side: THREE.DoubleSide} );
var base_plane = new THREE.Mesh( geometry, base_material );
base_plane.receiveShadow = true;
base_plane.castShadow = true;
scene.add( base_plane );
base_plane.position.z = -0.1;

var road_material = new THREE.MeshStandardMaterial( {color: 0x111111});//, side: THREE.DoubleSide} );

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

scene.background = new THREE.Color( 0x000000 );
init();

function init() {
    ROADS.add_road_network(base_plane,links,road_width,road_material,line_material)
    // calibrate_camera();

    window.addEventListener( 'resize', onWindowResize, false );
    onWindowResize();
    window.addEventListener('keypress', function(e) { manage_keypress(camera,e) });

    MODELS.add_model('blue-jeep/Jeep.gltf',[1,-1,0],[Math.PI/2.,0,0],0.05,scene)
    MODELS.add_model('yellow-jeep/1385 Jeep.gltf',[1,2,0],[Math.PI/2.,0,0],0.01,scene)
}
var last = 0 ;
function animate(now) {
    requestAnimationFrame( animate );
    line_material.resolution.set( window.innerWidth, window.innerHeight ); // resolution of the viewport

    if(!last || now - last >= 3000) { // every 5 seconds
        last = now;
        // on new heights from server:
        // ROADS.update_displacement_map(base_material,server_url,W,H);
        ROADS.fake_update_displacement_map(base_material,server_url,W,H);
    }
    var T = 50; // period of rotation of sun
    sun.position.x = 2*W*Math.sin(clock.getElapsedTime()*2.*Math.PI/T);
    sun.position.z = 2*W*Math.cos(clock.getElapsedTime()*2.*Math.PI/T);
    // console.log(sun.rotation)
    renderer.render( scene, camera );
};

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
}

animate();
