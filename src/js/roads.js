import * as THREE from './node_modules/three/build/three.module.js';
import { LineGeometry } from './node_modules/three/examples/jsm/lines/LineGeometry.js';
import { Line2 } from './node_modules/three/examples/jsm/lines/Line2.js';


function generate_regular_roads(W,H,R,B) {
    // W = 25 // half width in LEGO studs (x direction)
    // H = 25 // half height in LEGO studs (y direction)
    // R = 1 // half width of roads in studs
    // B = 4 // one block is 4 LEGO studs
    var z = 0.5;// small offset to help in general
    var links = [];
    links.push([[-W+R, H-R,z],[ W-R, H-R,z]]); // top boundary
    links.push([[-W+R,-H+R,z],[ W-R,-H+R,z]]); // bottom boundary
    links.push([[-W+R,-H+R,z],[-W+R, H-R,z]]); // left boundary
    links.push([[ W-R,-H+R,z],[ W-R, H-R,z]]); // right boundary

    for ( var i=-W+B+3*R;i<W-R;i+=B+2*R ) {
        links.push([[i, H-R,z],[i,-H+R,z]]); // vertical roads
    }
    for ( var i=-H+B+3*R;i<H-R;i+=B+2*R ) {
        links.push([[W-R,i,z],[-W+R,i,z]]); // horizontal roads
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

function add_road_segment(parent,pts,R,road_material) {
    var L = Math.abs(pts[1][0]-pts[0][0]) + 2*R;
    var H = Math.abs(pts[1][1]-pts[0][1]) + 2*R;
    // if (L > 0) { L += 2*R; }
    // if (H > 0) { H += 2*R; }
    // console.log(L,H);
    var geometry = new THREE.PlaneGeometry( L, H );
    var road = new THREE.Mesh( geometry, road_material );
    road.position.x = (pts[1][0]+pts[0][0])/2.;
    road.position.y = (pts[1][1]+pts[0][1])/2.;
    road.position.z = pts[1][2]/2.; // just half the offset
    road.receiveShadow = true;
    parent.add( road );


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

function add_line_marking_segment(parent,pts,line_material) {
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
    parent.add( line );
}

function add_road_network(parent,links,R,road_material,line_material) {
    links.forEach(function(pts, index, array) {
        add_road_segment(parent,pts,R,road_material);
    });
    links.forEach(function(pts, index, array) {
        add_line_marking_segment(parent,pts,line_material);
    });
}

function update_displacement_map(base_material,server_url,W,H) {
    var width = Math.floor(2*W);
    var height = Math.floor(2*H);
    // var size = width * height;
    // var arr = new Uint8Array( 3*size );
    // for ( var i = 0; i < size; i ++ ) {
    //     arr[ i*3+0 ] = Math.floor(Math.random()*255); // just red channel
    // }
    // var texture = new THREE.DataTexture( arr, width, height, THREE.RGBFormat );
    // base_material.displacementMap = texture;
    // base_material.displacementScale = 1;
    // base_material.needsUpdate = true;

    var scale = 200*9.6/8.; // to get height in stud widths (threejs in units of stud witdth)
    fetch(server_url+'/get_depths_from_server')
    .then( function(response) { return response.json(); })
    .then( function(data) {
        // console.log(data);
        data = data.flat();
        // data = JSON.parse(data);
        var arr = new Uint8Array( 3*data.length );
        for ( var i = 0; i < data.length; i ++ ) {
            // console.log(Math.floor(parseFloat(data[i])));
            // console.log(data[i])
            if ( data[i] >= 0 ) {
                arr[ i*3 ] = Math.floor(data[i]); // just red channel
            }
            else {
                arr[ i*3 ] = 0;
            }
        }
        // console.log(arr)

        var texture = new THREE.DataTexture( arr, width, height, THREE.RGBFormat );

        base_material.displacementMap = texture;
        base_material.displacementScale = scale;
        // base_material.displacementBias = -100;
        base_material.needsUpdate = true;
    })
    .catch(function(e) {
      console.log(e)
      console.log("Failed to get depths from server");
    });
}

function fake_update_displacement_map(base_material,server_url,W,H) {
    var width = Math.floor(2*W);
    var height = Math.floor(2*H);

    var scale = 255*(9.6/8.0) // to get height in stud widths (threejs in units of stud witdth)
    var data;
    data = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1,1,1,0,0,2,2,2,0,0],
            [0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1,1,1,0,0,2,2,2,0,0],
            [0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1,1,1,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,5,5,5,5,0,0,2,2,3,3,0,0,1,1,1,1,0,0,2,2,2,0,0],
            [0,0,5,5,5,5,0,0,2,2,3,3,0,0,1,1,1,1,0,0,2,2,2,0,0],
            [0,0,5,5,5,5,0,0,2,2,3,3,0,0,1,1,1,1,0,0,1,1,2,0,0],
            [0,0,5,5,5,5,0,0,2,2,3,3,0,0,3,1,1,1,0,0,1,1,2,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,2,2,2,2,0,0,2,2,2,2,0,0,3,3,3,3,0,0,1,1,1,0,0],
            [0,0,2,2,2,2,0,0,2,2,2,2,0,0,3,3,3,3,0,0,1,1,1,0,0],
            [0,0,2,2,2,2,0,0,2,2,2,2,0,0,2,2,1,1,0,0,1,1,1,0,0],
            [0,0,2,2,2,2,0,0,1,1,1,1,0,0,2,2,1,1,0,0,1,1,1,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,1,1,1,1,0,0,2,2,2,2,0,0,1,1,1,1,0,0,1,1,1,0,0],
            [0,0,1,1,1,1,0,0,2,2,2,2,0,0,1,1,1,1,0,0,1,1,1,0,0],
            [0,0,1,1,1,1,0,0,2,2,2,2,0,0,1,1,1,1,0,0,1,1,1,0,0],
            [0,0,1,1,1,1,0,0,2,2,2,2,0,0,1,1,1,1,0,0,1,1,1,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

    data = data.reverse().flat()
    var arr = new Uint8Array( 3*data.length );
    for ( var i = 0; i < data.length; i ++ ) {
        arr[ i*3 ] = data[i]; // just red channel
    }

    var texture = new THREE.DataTexture( arr, width, height, THREE.RGBFormat );

    base_material.displacementMap = texture;
    base_material.displacementScale = scale;
    base_material.needsUpdate = true;
}

export { add_road_network, generate_regular_roads, update_displacement_map, fake_update_displacement_map };
