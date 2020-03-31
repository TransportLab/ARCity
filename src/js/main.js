function add_road_segment(pts) {
    var L = Math.abs(pts[1][0]-pts[0][0]);
    var H = Math.abs(pts[1][1]-pts[0][1]);
    if (L > 0) { L += 1; }
    if (H > 0) { H += 1; }
    var geometry = new THREE.PlaneGeometry( L, H );
    var road = new THREE.Mesh( geometry, road_material );
    road.position.x = (pts[1][0]+pts[0][0])/2.;
    road.position.y = (pts[1][1]+pts[0][1])/2.;
    scene.add( road );


    // var geometry = new LineGeometry();
    // geometry.setPositions( pts.flat() );
    // var road = new Line2( geometry, road_material );
    // road.computeLineDistances();
    // road.scale.set( 1, 1, 1 );
    // scene.add( road );

    // var line_material = new LineMaterial( {
    //     color: 0xFF0000,
    //     linewidth: 0.005, // in pixels??????
    //     vertexColors: false,
    //     //resolution:  // to be set by renderer, eventually
    //     dashed: true,
    //     dashScale: 0.0001,
    //     // dashSize: 0.01,
    //     // gapSize: 0.01,
    // } );
    // var line = new Line2( geometry, line_material );
    // line.computeLineDistances();
    // line.scale.set( 1, 1, 1 );
    // scene.add( line );
}

function add_line_marking_segment(pts) {
    // WEBGL METHOD - only makes single pixel wide lines
    // var points = [];
    // points.push( new THREE.Vector3( pts[0][0], pts[0][1], pts[0][2] ) );
    // points.push( new THREE.Vector3( pts[1][0], pts[1][1], pts[1][2] ) );
    //
    // var geometry = new THREE.BufferGeometry().setFromPoints( points );
    // var line = new THREE.Line( geometry, road_paint_material );
    // line.computeLineDistances();
    // scene.add( line );

    var geometry = new LineGeometry();
    geometry.setPositions( pts.flat() );
    var line = new Line2( geometry, line_material );
    line.computeLineDistances();
    line.scale.set( 1, 1, 1 );
    scene.add( line );
}

function add_road_network(links) {
    links.forEach(function(pts, index, array) {
        add_road_segment(pts);
    });
    links.forEach(function(pts, index, array) {
        add_line_marking_segment(pts);
    });
}

function calibrate_camera() {
    var calibrated = false
    while ( !calibrated ) {

    }
}

function loss(X) {

}

function locate_domain() {
    var threshold = 999
    while ( threshold > 1 ) {
        // project four red circles
        // find them with the camera
        // calculate error between true loc and projected loc
        // optimize... maybe something like this: https://github.com/benfred/fmin
        var solution = fmin.nelderMead(loss, locs);
        // console.log("solution is at " + solution.x);
    }
}

import * as THREE from './node_modules/three/build/three.module.js';
import { LineGeometry } from './node_modules/three/examples/jsm/lines/LineGeometry.js';
import { LineMaterial } from './node_modules/three/examples/jsm/lines/LineMaterial.js';
import { Line2 } from './node_modules/three/examples/jsm/lines/Line2.js';
import { OrbitControls } from './node_modules/three/examples/jsm/controls/OrbitControls.js';
// import { nelderMead } from './node_modules/fmin/src/nelderMead.js'

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );
camera.position.z = 20;

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );
// var controls = new OrbitControls( camera, renderer.domElement );



var geometry = new THREE.PlaneGeometry( 25, 25, 32 );
var base_material = new THREE.MeshBasicMaterial( {color: 0xffffff, side: THREE.DoubleSide} );
var base_plane = new THREE.Mesh( geometry, base_material );
scene.add( base_plane );
base_plane.position.z = -0.1;

var road_material = new THREE.MeshBasicMaterial( {color: 0x000000, side: THREE.DoubleSide} );

var line_material = new LineMaterial( {
    color: 0xFFFFFF,
    linewidth: 3, // in pixels??????
    // vertexColors: false,
    //resolution:  // to be set by renderer, eventually
    dashScale: 5,
    gapSize: 3,
    dashSize: 4
} );
line_material.defines.USE_DASH = ""; // enables dashing

var links = [[[-12,-12,0],[-12, 12,0]],
             [[-12,-12,0],[ 12,-12,0]],
             [[ 12, 12,0],[ 12,-12,0]],
             [[ 12, 12,0],[-12, 12,0]],
             [[-12,  0,0],[ 12,  0,0]], // horizontal middle
             [[  0,-12,0],[  0, 12,0]], // vertical middle
         ];

// locate_domain()

scene.background = new THREE.Color( 0xFF0000 );
init();

function init() {
    add_road_network(links)
    // calibrate_camera();

    window.addEventListener( 'resize', onWindowResize, false );
    onWindowResize();
    window.addEventListener('keypress', manage_keypress);
}

function manage_keypress(e) {
  if ( e.key === 'w') { camera.position.y -= 0.1; }
  else if ( e.key === 'a') { camera.position.x += 0.1; }
  else if ( e.key === 's') { camera.position.y += 0.1; }
  else if ( e.key === 'd') { camera.position.x -= 0.1; }
  else if ( e.key === 'q') { camera.position.z += 0.1; }
  else if ( e.key === 'e') { camera.position.z -= 0.1; }
  else if ( e.key === 'r') { camera.rotation.x += 0.01; }
  else if ( e.key === 'f') { camera.rotation.x -= 0.01; }
  else if ( e.key === 't') { camera.rotation.y += 0.01; }
  else if ( e.key === 'g') { camera.rotation.y -= 0.01; }
  else if ( e.key === 'y') { camera.rotation.z += 0.01; }
  else if ( e.key === 'h') { camera.rotation.z -= 0.01; }
}

var animate = function () {
    requestAnimationFrame( animate );
    // renderer.setClearColor( 0x000000, 0 );
	// renderer.setViewport( 0, 0, window.innerWidth, window.innerHeight );
    line_material.resolution.set( window.innerWidth, window.innerHeight ); // resolution of the viewport


    // base_plane.rotation.x += 0.01;
    // base_plane.rotation.y += 0.01;

    renderer.render( scene, camera );
};

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
}

animate();
