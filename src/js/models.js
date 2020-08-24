import * as THREE from './node_modules/three/build/three.module.js';
import { GLTFLoader } from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';

function add_model(file,rot,scale,parent,G,link,cars,R) {
    new GLTFLoader()
    .load( '../models/' + file, function ( gltf ) {
        gltf.scene.traverse( function( node ) {
            if ( node.isMesh ) { node.castShadow = true; }
        } );
        var mesh = gltf.scene;
        // earth.applyMatrix( new THREE.Matrix4().makeTranslation( 0, -27., 0 ) );
        mesh.scale.set(scale,scale,scale);
        mesh.rotateX(rot[0]);
        mesh.rotateY(rot[1]);
        mesh.rotateZ(rot[2]);
        mesh.receiveShadow = true;
        mesh.castShadow = true;
        // console.log(rot)
        // console.log(mesh.rotation)

        // ALL MESHES SHOULD BE POINTING HORIZONTALL (FACING TO THE RIGHT)
        // AND LOCATED AT (0,0,0) LOOKING GOOD ON THE ROAD,
        // RIGHT OVER THE LANE INTERSECTION MARKINGS

        var car = new THREE.Object3D();
        car.add( mesh );
        mesh.position.x = R/2.; // put on left side of road

        var nodes = get_nodes_from_link(G,link)
        assign_to_nodes(G,nodes,car)
        // assign_to_link(G,link,car);
        car.position.set((car.nodes_x[0] + car.nodes_x[1])/2.,
                         (car.nodes_y[0] + car.nodes_y[1])/2.,
                         0);
        car.isturning = false;
        car.making_left_turn = false;

        parent.add( car );

        cars.push(car);
       }
   );
}

function pick_new_link(G,car,node) {
    var potential_edges = G.edges(car.nodes[node])// get all edges at node
    var choice = Math.floor(Math.random() * potential_edges.length);
    // Get position in flattened edge array, assuming they are sorted and ordered and 5xN...
    var new_edge = potential_edges[0][choice][0]*5 + potential_edges[0][choice][1];

    // console.log(car.nodes[node])
    // console.log(potential_edges)
    return new_edge
}

function pick_target_node(G,car,node) {
    var new_nodes = [[0,0],[0,0]];
    while ((new_nodes[0][0] === new_nodes[1][0]) && (new_nodes[0][1] === new_nodes[1][1])) {
        var potential_edges = G.edges(car.nodes[1])// get all edges at node
        // console.log(potential_edges)
        var choice = Math.floor(Math.random() * (potential_edges.length));
        // console.log(Math.random() * potential_edges.length);
        // console.log(choice,potential_edges.length);
        // console.log(potential_edges[choice])
        var new_nodes = [car.nodes[1],potential_edges[choice][1]];
    }
    // var nodes = G.edges(true)[new_edge]; // nearby nodes corresponding to link
    // var x_0 = G.node.get(nodes[0]).x
    // var x_1 = G.node.get(nodes[1]).x
    // var y_0 = G.node.get(nodes[0]).y
    // var y_1 = G.node.get(nodes[1]).y
    // console.log('Currently at ')
    // console.log(G.node.get(car.nodes[node]))
    // console.log('Want destination')
    // console.log(G.node.get(potential_edges[0][choice]))
    // console.log('Picked the following link:')
    // console.log(x_0,x_1,y_0,y_1)
    // console.log(new_nodes);
    return new_nodes
}

function get_nodes_from_link(G,link){
    var nodes = G.edges(true)[link]; // nearby nodes corresponding to link
    return nodes
}

function assign_to_nodes(G,nodes,car) {
    car.isturning = true;
    car.angle_before_turning = car.rotation.z;
    // console.log(nodes)
    var x_0 = G.node.get(nodes[0]).x
    var x_1 = G.node.get(nodes[1]).x
    var y_0 = G.node.get(nodes[0]).y
    var y_1 = G.node.get(nodes[1]).y
    // window.source.position.x = x_0;
    // window.source.position.y = y_0;
    // window.dest.position.x = x_1;
    // window.dest.position.y = y_1;

    // console.log(x_0,y_0,x_1,y_1)

    car.nodes = nodes;
    // console.log(nodes)
    car.nodes_x = [x_0,x_1];
    car.nodes_y = [y_0,y_1];
    // console.log(car.nodes_x);
    // console.log(car.nodes_y);
    // var node_0_dist = Math.sqrt(Math.pow((x_0 - car.position.x),2) + Math.pow((y_0 - car.position.y),2));
    // var node_1_dist = Math.sqrt(Math.pow((x_1 - car.position.x),2) + Math.pow((y_1 - car.position.y),2));
    // var node_dists = [node_0_dist,node_1_dist];
    // var nearby_node_index = node_dists.indexOf(Math.min(...node_dists));
    // console.log(nearby_node_index);
    if ( x_0 === x_1 ) { // link is vertical
        // car.direction = Math.sign(car.nodes_y[1-nearby_node_index]-car.nodes_y[nearby_node_index]);
        car.direction = Math.sign(car.nodes_y[1]-car.nodes_y[0])
        // console.log(car.direction);
        car.orientation = 'v'
        // car.rotation.set(0,0,(car.direction+1)/2.*Math.PI);
        car.angle_after_turning = (car.direction+1)/2.*Math.PI
        // car.position.x = x_0;
    }
    else if (y_0 === y_1) { // link is horizontal
        // car.direction = Math.sign(car.nodes_x[1-nearby_node_index]-car.nodes_x[nearby_node_index]);
        car.direction = Math.sign(car.nodes_x[1]-car.nodes_x[0])
        car.orientation = 'h';
        // car.rotation.set(0,0, Math.PI/2. + (car.direction-1)/2.*Math.PI );
        car.angle_after_turning = Math.PI/2. + (car.direction-1)/2.*Math.PI;
        // car.position.y = y_0;
    }
    else {
        console.log([x_0,y_0,x_1,y_1]);
    }
    var diff = (car.angle_after_turning - car.angle_before_turning)/Math.PI*180;
    car.signed_angle_to_turn = mod(diff + 180, 360) - 180;


    // NEED TO DO SOMETHING DIFFERENT FOR LEFT TURNS!!!!
}
function mod(a, n) {
    return a - Math.floor(a/n) * n
}

function turn_car(car,R) {
    // just getting started
    if ( car.rotation.z === car.angle_before_turning ) {
        if ( car.signed_angle_to_turn === 90 )  { // left turn
            car.making_left_turn = true;
            console.log('Making left turn');
            // if ( car.angle_before_turning === 0 ) {
                // car.children[0].position.x = -R/2.;
                // car.position.x -= R/2.;
            // }


        }
    }
    var dtheta = 2.;
    if ( Math.abs(car.signed_angle_to_turn - dtheta*Math.sign(car.signed_angle_to_turn)) > 0 ) {
        car.signed_angle_to_turn -= dtheta*Math.sign(car.signed_angle_to_turn);
        car.rotateZ(dtheta*Math.sign(car.signed_angle_to_turn)*Math.PI/180.);
    }
    else {
        car.rotation.set(0,0,car.angle_after_turning);
        car.signed_angle_to_turn = 0;
        car.isturning = false;
        if ( car.making_left_turn ) {
            // car.making_left_turn = false;
            // car.children[0].position.x = R/2.;
            // car.position.x += R/2.;
            // console.log('Left turn done');
        }
    }
    // console.log(car.signed_angle_to_turn);
}
// export { add_model, assign_to_link, pick_new_link, pick_target_node, assign_to_nodes, get_nodes_from_link };
export { add_model, pick_target_node, assign_to_nodes, get_nodes_from_link, turn_car };
