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
var projector_throw_ratio = 2.0; // width of projected area / distance to
var projector_plane_distance_mm = 1000.0; // distance in mm
var projector_plane_distance_studs = projector_plane_distance_mm/mm_per_stud; // distance in mm
var projector_aspect_ratio = 16./9.

var W = 25/2. // half width in LEGO studs (x direction)
var H = 25/2. // half height in LEGO studs (y direction)
var road_width = 2/2 // half width of roads in studs
var block_length = 4 // one block is 4 LEGO studs
var server_url = 'http://localhost:5000'

var clock = new THREE.Clock();
var scene = new THREE.Scene();
// var camera = new THREE.PerspectiveCamera( 50, window.innerWidth/window.innerHeight, 0.1, 1000 ); // vertical FOV angle, aspect ratio, near, far
var fov_vertical = 2*Math.atan(projector_aspect_ratio/projector_throw_ratio/2.)*(180/Math.PI); // approx 59 degrees for a 0.5 throw ratio
var camera = new THREE.PerspectiveCamera( fov_vertical, window.innerWidth/window.innerHeight, 0.1, 1000 ); // vertical FOV angle, aspect ratio, near, far
// camera.position.z = projector_plane_distance_studs;
// camera.position.y = -projector_plane_distance_studs/projector_throw_ratio/projector_aspect_ratio; // vertical offset`
camera.position.x = 0;
camera.position.y = 0;
camera.position.z = 30;

// camera.rotation.x = -fov_vertical*Math.PI/180./2.; // half FOV angle - but then I need to rotate the plane back??
// console.log(camera.rotation.x)
// var ambient_light = new THREE.AmbientLight( 0xFFFFFF ); // white light
// scene.add( ambient_light );
var sunGeometry = new THREE.SphereBufferGeometry( 0.1 ); // radius
var sunMat = new THREE.MeshStandardMaterial( {
					emissive: 0xffffee,
					emissiveIntensity: 1,
					color: 0x000000
				} );
var sun = new THREE.PointLight( 0xFFFFFF, 1, 0, 2 ); // white light
// sun.add( new THREE.Mesh( sunGeometry, sunMat ) );
sun.castShadow = true;
scene.add( sun );
// sun.shadow.mapSize.width = 512*2;  // default
// sun.shadow.mapSize.height = 512*2; // default
sun.position.x = 0.5;
sun.position.y = 0.5;
sun.position.z = 1;

var renderer = new THREE.WebGLRenderer();
renderer.shadowMap.enabled = true;
renderer.setPixelRatio( window.devicePixelRatio );
renderer.setSize( window.innerWidth, window.innerHeight );
// renderer.gammaOutput = true;
// renderer.gammaFactor = 2.2;
document.body.appendChild( renderer.domElement );
var controls = new OrbitControls( camera, renderer.domElement );

var geometry = new THREE.PlaneGeometry( 2*W, 2*H,Math.floor(2*W*10),Math.floor(2*H*10));
var base_material = new THREE.MeshStandardMaterial( {color: 0xFFFFFF, side: THREE.DoubleSide} );
var base_plane = new THREE.Mesh( geometry, base_material );
base_plane.receiveShadow = true;
base_plane.castShadow = true;
scene.add( base_plane );
base_plane.position.z = 0;//-0.01;

var road_material = new THREE.MeshStandardMaterial( {color: 0x000000});//, side: THREE.DoubleSide} );

var line_material = new LineMaterial( {
    color: 0xFFFFFF,
    linewidth: 2, // in pixels??????
    dashScale: 5,
    gapSize: 3,
    dashSize: 4
} );
line_material.defines.USE_DASH = ""; // enables dashing

var links = ROADS.generate_regular_roads(W,H,road_width,block_length)
var G = ROADS.generate_regular_roads_networkx(W,H,road_width,block_length)
window.G = G;
// locate_domain()
var cars = [];
var last = 0 ;
scene.background = new THREE.Color( 0x000000 );
init();
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
    ROADS.add_road_network(base_plane,links,road_width,road_material,line_material)
    // calibrate_camera();

    window.addEventListener( 'resize', onWindowResize, false );
    onWindowResize();
    window.addEventListener('keypress', function(e) { manage_keypress(camera,e) });
    //                file,                       rot,            scale,parent,G,link,cars,R
    for (var i=0;i<20;i=i+2) {
        MODELS.add_model('yellow-jeep/1385 Jeep.gltf',[Math.PI/2.,0,0],0.01,scene,G,i,cars,road_width);
        MODELS.add_model('blue-jeep/Jeep.gltf',       [Math.PI/2.,0,0],0.05,scene,G,i+1,cars,road_width);
    }

}

function animate(now) {
    var dt = clock.getDelta()
    requestAnimationFrame( animate );
    line_material.resolution.set( window.innerWidth, window.innerHeight ); // resolution of the viewport

    if(!last || now - last >= 1000) { // every 5 seconds
        last = now;
        // on new heights from server:
        // ROADS.update_displacement_map(base_material,server_url,W,H);
        ROADS.fake_update_displacement_map(base_material,server_url,W,H);
    }
    var T = 50000; // period of rotation of sun
    sun.position.x = 2*W*Math.sin(clock.getElapsedTime()*2.*Math.PI/T);
    sun.position.z = 2*W*Math.cos(clock.getElapsedTime()*2.*Math.PI/T);
    // console.log(sun.rotation)

    var speed = 2; // vehicle speed
    cars.forEach( function(car, index) {
        // console.log(car.direction)
        ROADS.check_for_intersection(G,car,road_width)
        if ( car.orientation === 'h' ) { car.position.x += car.direction*speed*dt; }
        else if ( car.orientation === 'v' ) { car.position.y += car.direction*speed*dt; }
        else { console.log('Orientation not defined. Not moving.'); }
    });
    // console.log(cars);


    renderer.render( scene, camera );
};

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
}

animate();
