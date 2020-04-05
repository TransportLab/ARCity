import * as THREE from './node_modules/three/build/three.module.js';
import { GLTFLoader } from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';

function add_model(file,rot,scale,parent,G,link,direction,cars,R) {
    new GLTFLoader()
    .load( '../models/' + file, function ( gltf ) {
        gltf.scene.traverse( function( node ) {
            if ( node.isMesh ) { node.castShadow = true; }
        } );
        var mesh = gltf.scene;
        mesh.direction = direction;
        // earth.applyMatrix( new THREE.Matrix4().makeTranslation( 0, -27., 0 ) );
        mesh.scale.set(scale,scale,scale);
        mesh.rotateX(rot[0]);
        mesh.rotateY(rot[1]);
        mesh.rotateZ(rot[2]);

        assign_to_edge(G,link,mesh);
        mesh.position.set((mesh.nodes_x[0] + mesh.nodes_x[1])/2.,
                          (mesh.nodes_y[0] + mesh.nodes_y[1])/2.,
                          0);

        mesh.receiveShadow = true;
        mesh.castShadow = true;
        // console.log(rot)
        // console.log(mesh.rotation)
        parent.add( mesh );

        cars.push(mesh);
       }
   );
}

function pick_new_edge(G,car,node) {
    var potential_edges = G.edges(car.nodes[node])// get all edges at node 0
    var choice = Math.floor(Math.random() * potential_edges.length);
    var new_edge = potential_edges[0][choice][0]*5 + potential_edges[0][choice][1];
    car.direction = Math.floor(Math.random() * 2 )*2 - 1;
    return new_edge
}

function assign_to_edge(G,link,mesh,R) {
    var nodes = G.edges(true)[link]; // nearby nodes corresponding to link
    var x_0 = G.node.get(nodes[0]).x
    var x_1 = G.node.get(nodes[1]).x
    var y_0 = G.node.get(nodes[0]).y
    var y_1 = G.node.get(nodes[1]).y

    mesh.nodes = nodes;
    mesh.nodes_x = [x_0,x_1];
    mesh.nodes_y = [y_0,y_1];

    if ( x_0 === x_1 ) { // link is vertical
        mesh.rotateY((mesh.direction+1)/2.*Math.PI);
        mesh.orientation = 'v'
        mesh.position.x += R/2.*mesh.direction;
    }
    else { // link is vertical
        mesh.rotateY(Math.PI/2. + (mesh.direction-1)/2.*Math.PI);
        mesh.orientation = 'h'
        mesh.position.y += R/2.*mesh.direction;
    }
}

export { add_model, assign_to_edge, pick_new_edge };
