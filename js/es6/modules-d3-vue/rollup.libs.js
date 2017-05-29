import resolve from 'rollup-plugin-node-resolve';
import babel from 'rollup-plugin-babel';
//import uglify from 'rollup-plugin-uglify';

export default {
  entry: 'src/libs/index.js',
  format: 'iife',
  plugins: [ resolve(), babel({exclude: 'node_modules/**'}) ],
  dest: 'dist/js/libs.js',
  moduleName: 'libs',
  //sourceMap: true
};