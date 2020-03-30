function add_road_segment(pts) {
    var geometry = new LineGeometry();
    geometry.setPositions( pts.flat() );

    var road_material = new LineMaterial( {
        color: 0x000000,
        linewidth: 0.035, // in pixels??????
        vertexColors: false,
        //resolution:  // to be set by renderer, eventually
        dashed: false
    } );

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
    //
    var road = new Line2( geometry, road_material );
    road.computeLineDistances();
    road.scale.set( 1, 1, 1 );
    scene.add( road );
    // var line = new Line2( geometry, line_material );
    // line.computeLineDistances();
    // line.scale.set( 1, 1, 1 );
    // scene.add( line );
}

function add_line_marking_segment(pts) {
    var road_paint_material = new THREE.LineDashedMaterial({
        color: 0xFFFFFF,
        linewidth: 50, // doesn't seem to do anything
        scale: 1,
        dashSize: 0.5,
        gapSize: 0.5});

    var points = [];
    points.push( new THREE.Vector3( pts[0][0], pts[0][1], pts[0][2] ) );
    points.push( new THREE.Vector3( pts[1][0], pts[1][1], pts[1][2] ) );

    var geometry = new THREE.BufferGeometry().setFromPoints( points );
    var line = new THREE.Line( geometry, road_paint_material );
    line.computeLineDistances();
    scene.add( line );
}

import * as THREE from './node_modules/three/build/three.module.js';
import { LineGeometry } from './node_modules/three/examples/jsm/lines/LineGeometry.js';
import { LineMaterial } from './node_modules/three/examples/jsm/lines/LineMaterial.js';
import { Line2 } from './node_modules/three/examples/jsm/lines/Line2.js';

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );
camera.position.z = 20;

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

var geometry = new THREE.PlaneGeometry( 25, 25, 32 );
var material = new THREE.MeshBasicMaterial( {color: 0xffffff, side: THREE.DoubleSide} );
var base_plane = new THREE.Mesh( geometry, material );
scene.add( base_plane );

var links = [[[-12,-12,0],[-12, 12,0]],
             [[-12,-12,0],[ 12,-12,0]],
             [[ 12, 12,0],[ 12,-12,0]],
             [[ 12, 12,0],[-12, 12,0]],
             [[-12,  0,0],[ 12,  0,0]], // horizontal middle
             [[  0,-12,0],[  0, 12,0]], // vertical middle
         ];

links.forEach(function(pts, index, array) {
    add_road_segment(pts);
})
links.forEach(function(pts, index, array) {
    add_line_marking_segment(pts);
})





var animate = function () {
    requestAnimationFrame( animate );

    // base_plane.rotation.x += 0.01;
    // base_plane.rotation.y += 0.01;

    renderer.render( scene, camera );
};

animate();
