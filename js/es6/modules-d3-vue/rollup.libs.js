import resolve from 'rollup-plugin-node-resolve';
//import uglify from 'rollup-plugin-uglify';

export default {
  entry: 'src/libs/index.js',
  format: 'iife',
  plugins: [ resolve() ],
  dest: 'dist/js/libs.js',
  moduleName: 'libs',
  //sourceMap: true
};