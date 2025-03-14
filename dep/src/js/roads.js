import { LineGeometry } from 'three/examples/jsm/lines/LineGeometry.js';
import { Line2 } from 'three/examples/jsm/lines/Line2.js';
import * as NETWORKX from './jsnetworkx.js'
import * as MODELS from './models.js';
import { Lut } from './Lut.js';

let line_markings = new THREE.Group();
let road_segments = new THREE.Group();
var lut = new Lut("rkg", 512);
lut.setMin(2);
lut.setMax(3);
let links = [];
export let G;

let heights = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1,1,1,0,0,2,2,2,0,0],
    [0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1,1,1,0,0,2,2,2,0,0],
    [0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1,1,1,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,4,4,4,4,0,0,2,2,3,3,0,0,1,1,1,1,0,0,2,2,2,0,0],
    [0,0,4,4,4,4,0,0,2,2,3,3,0,0,1,1,1,1,0,0,2,2,2,0,0],
    [0,0,4,4,4,4,0,0,2,2,3,3,0,0,1,1,1,1,0,0,1,1,2,0,0],
    [0,0,4,4,4,4,0,0,2,2,3,3,0,0,3,1,1,1,0,0,1,1,2,0,0],
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
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

function update_traffic_randomly(min_speed,max_speed,parent) {
    G.edges(true).forEach( function(edge, index) {
        var speed = min_speed + Math.random()*(max_speed - min_speed);
        G.adj.get(edge[0]).get(edge[1]).speed = speed;
        road_segments.children[index].material.color = lut.getColor(speed);
        // if ( index < parent.children.length ) {
        //     parent.children[index].material.color = lut.getColor(speed);
        // }
    });
    // parent.children[0].children[Math.floor(Math.random()*parent.children[0].children.length)].material.color = lut.getColor(min_speed + Math.random()*(max_speed - min_speed));
}

// function generate_regular_roads(W,H,R,B) {
//     // W = 25 // half width in LEGO studs (x direction)
//     // H = 25 // half height in LEGO studs (y direction)
//     // R = 1 // half width of roads in studs
//     // B = 4 // one block is 4 LEGO studs
//     var z = 0.05;// small offset to help in general
//     links.push([[-W+R, H-R,z],[ W-R, H-R,z]]); // top boundary
//     links.push([[-W+R,-H+R,z],[ W-R,-H+R,z]]); // bottom boundary
//     links.push([[-W+R,-H+R,z],[-W+R, H-R,z]]); // left boundary
//     links.push([[ W-R,-H+R,z],[ W-R, H-R,z]]); // right boundary

//     for ( var i=-W+B+3*R;i<W-R;i+=B+2*R ) {
//         links.push([[i, H-R,z],[i,-H+R,z]]); // vertical roads
//     }
//     for ( var i=-H+B+3*R;i<H-R;i+=B+2*R ) {
//         links.push([[W-R,i,z],[-W+R,i,z]]); // horizontal roads
//     }
//     // var links = [[[-12,-12,0],[-12, 12,0]],
//     //              [[-12,-12,0],[ 12,-12,0]],
//     //              [[ 12, 12,0],[ 12,-12,0]],
//     //              [[ 12, 12,0],[-12, 12,0]],
//     //              [[-12,  0,0],[ 12,  0,0]], // horizontal middle
//     //              [[  0,-12,0],[  0, 12,0]], // vertical middle
//     //          ];
// }

function generate_regular_roads_networkx(W,H,R,B,parent,road_material,line_material) {
    // This creates a new empty, undirected graph
    // var G = new jsnx.Graph();
    var m = Math.ceil((2*W-2*R)/(B+2*R))+1; // number of blocks in x direction
    var n = Math.ceil((2*H-2*R)/(B+2*R))+1; // number of blocks in y direction

    G = NETWORKX.grid2dGraph(m,n);

    var i = 0; var x = -W + R;
    while ( i < m ) {
        var j = 0; var y = -H + R;
        while ( j < n) {
            G.addNode([i,j], {x: x, y: y});
            j += 1
            if ( y + B + 2*R > H-R ) { y = H - R; }
            else { y += B + 2*R; }
            // console.log(x,y)
        }
        i += 1
        if ( x + B + 2*R > W-R ) { x = W - R; }
        else { x += B + 2*R; }
    }
    
    // console.log(G.nodes(true)); // show all nodes
    // console.log(G.node.get([2,3]).x) // see x and y values here

    G.edges(true).forEach( function(edge, index) {
        let zoff = 0.1;//*Math.random();
        let pts = [
            [G.node.get(edge[0]).x, G.node.get(edge[0]).y, zoff],
            [G.node.get(edge[1]).x, G.node.get(edge[1]).y, zoff]
        ];
        add_road_segment(road_segments,pts,R,road_material);
        add_line_marking_segment(line_markings,pts,line_material);
    });
    console.log(road_segments)
    parent.add( road_segments );
    parent.add( line_markings );
    // console.log(parent)
}


function add_road_segment(parent,pts,R,road_material) {
    // // segments end at intersection
    // var L = Math.abs(pts[1][0]-pts[0][0]);// + 2*R;
    // var H = Math.abs(pts[1][1]-pts[0][1]);// + 2*R;
    // if (L == 0) { L += 2*R; }
    // if (H == 0) { H += 2*R; }
    // segments overlap with intersection
    var L = Math.abs(pts[1][0]-pts[0][0]) + 2*R;
    var H = Math.abs(pts[1][1]-pts[0][1]) + 2*R;
    // console.log(L,H);
    var geometry = new THREE.PlaneGeometry( L, H );
    var road = new THREE.Mesh( geometry, road_material.clone() );
    road.position.x = (pts[1][0]+pts[0][0])/2.;
    road.position.y = (pts[1][1]+pts[0][1])/2.;
    road.position.z = (pts[0][2] + pts[1][2])/4.; // less than the offset so that the lines go on top
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

// function add_road_network(parent,R,road_material,line_material) {
//     parent.add(road_segments);
//     links.forEach(function(pts, index, array) {
//         add_road_segment(road_segments,pts,R,road_material);
//     });

//     parent.add(line_markings);
//     links.forEach(function(pts, index, array) {
//         add_line_marking_segment(line_markings,pts,line_material);
//     });
// }

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

function fake_update_displacement_map(base_material,server_url,W,H,R,B) {
    var m = Math.ceil((2*W-2*R)/(B+2*R))+1; // number of blocks in x direction
    var n = Math.ceil((2*H-2*R)/(B+2*R))+1; // number of blocks in y direction

    var arr = new Uint8Array( 4*W*H );

    var i = 0; var x = -W + R;
    while ( i < m ) {
        var j = 0; var y = -H + R;
        while ( j < n) {
            let this_height = Math.floor(Math.random()*5);
            for ( var k=0;k<B-2*R;k++ ) {
                for ( var l=0;l<B-2*R;l++ ) {
                    arr[4*((i*B + k)*W+j*B+l)] = this_height;
                }
            }
            j += 1
            if ( y + B + 2*R > H-R ) { y = H - R; }
            else { y += B + 2*R; }
            // console.log(x,y)
        }
        i += 1
        if ( x + B + 2*R > W-R ) { x = W - R; }
        else { x += B + 2*R; }
    }

    var scale = 255*(9.6/8.0) // to get height in stud widths (threejs in units of stud witdth)
    
    var texture = new THREE.DataTexture( arr, W, H, THREE.RGBAFormat );
    texture.needsUpdate = true;

    base_material.displacementMap = texture;
    base_material.displacementScale = scale;
    base_material.needsUpdate = true;
    
}

function check_for_intersection(car,R) {
    if ( car.orientation === 'h' ) {
        if ( car.direction === -1 ) {
            if ( car.position.x <= car.nodes_x[1] ) {
                var new_nodes = MODELS.pick_target_node(G,car,0)
                MODELS.assign_to_nodes(G,new_nodes,car);
            }
            // else if ( car.position.x <= car.nodes_x[1] ) {
            //     var new_nodes = MODELS.pick_target_node(G,car,1)
            //     MODELS.assign_to_nodes(G,new_nodes,car);
            // }
        }
        else if ( car.direction === 1 ) {
            if ( car.position.x >= car.nodes_x[1] ) {
                var new_nodes = MODELS.pick_target_node(G,car,0)
                MODELS.assign_to_nodes(G,new_nodes,car);
            }
            // else if ( car.position.x >= car.nodes_x[1] ) {
            //     var new_nodes = MODELS.pick_target_node(G,car,1)
            //     MODELS.assign_to_nodes(G,new_nodes,car);
            // }
        }
    }
    if ( car.orientation === 'v' ) {
        if ( car.direction === -1 ) {
            if ( car.position.y <= car.nodes_y[1] ) {
                var new_nodes = MODELS.pick_target_node(G,car,0)
                MODELS.assign_to_nodes(G,new_nodes,car);
            }
            // else if ( car.position.y <= car.nodes_y[1] ) {
            //     console.log('v2');
            //     var new_nodes = MODELS.pick_target_node(G,car,1)
            //     MODELS.assign_to_nodes(G,new_nodes,car);
            // }
        }
        else if ( car.direction === 1 ) {
            if ( car.position.y >= car.nodes_y[1] ) {
                var new_nodes = MODELS.pick_target_node(G,car,0)
                MODELS.assign_to_nodes(G,new_nodes,car);
            }
            // else if ( car.position.y >= car.nodes_y[1] ) {
            //     console.log('v4');
            //     var new_nodes = MODELS.pick_target_node(G,car,1)
            //     MODELS.assign_to_nodes(G,new_nodes,car);
            // }
        }
    }
}

export { generate_regular_roads_networkx, update_displacement_map, fake_update_displacement_map, check_for_intersection, update_traffic_randomly };
