import * as THREE from './node_modules/three/build/three.module.js';
import { LineGeometry } from './node_modules/three/examples/jsm/lines/LineGeometry.js';
import { Line2 } from './node_modules/three/examples/jsm/lines/Line2.js';


function generate_regular_roads(W,H,R,B) {
    // W = 25 // half width in LEGO studs (x direction)
    // H = 25 // half height in LEGO studs (y direction)
    // R = 1 // half width of roads in studs
    // B = 4 // one block is 4 LEGO studs

    var links = [];
    links.push([[-W+R, H-R,0],[ W-R, H-R,0]]); // top boundary
    links.push([[-W+R,-H+R,0],[ W-R,-H+R,0]]); // bottom boundary
    links.push([[-W+R,-H+R,0],[-W+R, H-R,0]]); // left boundary
    links.push([[ W-R,-H+R,0],[ W-R, H-R,0]]); // right boundary

    for ( var i=-W+B+3*R;i<W-R;i+=B+2*R ) {
        links.push([[i, H-R,0],[i,-H+R,0]]); // vertical roads
    }
    for ( var i=-H+B+3*R;i<H-R;i+=B+2*R ) {
        links.push([[W-R,i,0],[-W+R,i,0]]); // horizontal roads
    }
    // var links = [[[-12,-12,0],[-12, 12,0]],
    //              [[-12,-12,0],[ 12,-12,0]],
    //              [[ 12, 12,0],[ 12,-12,0]],
    //              [[ 12, 12,0],[-12, 12,0]],
    //              [[-12,  0,0],[ 12,  0,0]], // horizontal middle
    //              [[  0,-12,0],[  0, 12,0]], // vertical middle
    //          ];
    return links
}

function add_road_segment(scene,pts,R,road_material) {
    var L = Math.abs(pts[1][0]-pts[0][0]) + 2*R;
    var H = Math.abs(pts[1][1]-pts[0][1]) + 2*R;
    // if (L > 0) { L += 2*R; }
    // if (H > 0) { H += 2*R; }
    // console.log(L,H);
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

function add_line_marking_segment(scene,pts,line_material) {
    // WEBGL METHOD - only makes single pixel wide lines
    // var points = [];
    // points.push( new THREE.Vector3( pts[0][0], pts[0][1], pts[0][2] ) );
    // points.push( new THREE.Vector3( pts[1][0], pts[1][1], pts[1][2] ) );
    //
    // var geometry = new THREE.BufferGeometry().setFromPoints( points );
    // var line = new THREE.Line( geometry, road_paint_material );
    // line.computeLineDistances();
    // scene.add( line );

    // LINEGEOMETRY METHOD
    var geometry = new LineGeometry();
    geometry.setPositions( pts.flat() );
    var line = new Line2( geometry, line_material );
    line.computeLineDistances();
    line.scale.set( 1, 1, 1 );
    scene.add( line );
}

function add_road_network(scene,links,R,road_material,line_material) {
    links.forEach(function(pts, index, array) {
        add_road_segment(scene,pts,R,road_material);
    });
    links.forEach(function(pts, index, array) {
        add_line_marking_segment(scene,pts,line_material);
    });
}

function update_displacement_map(base_material) {
    // could potentially add a displacement map to improve rendering fidelity of light/dark areas
    base_material.displacementMap = new THREE.Texture(canvas);
    base_material.displacementScale = 30;
}

export { add_road_network, generate_regular_roads, update_displacement_map };
