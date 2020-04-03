import * as THREE from './node_modules/three/build/three.module.js';
import { GLTFLoader } from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';

function add_model(file,loc,rot,scale,parent,cars) {
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
        mesh.position.set(loc[0],loc[1],loc[2]);
        mesh.receiveShadow = true;
        mesh.castShadow = true;
        // console.log(rot)
        // console.log(mesh.rotation)
        parent.add( mesh );

        cars.push(mesh);
       }
   );
}

export { add_model };
