import resolve from 'rollup-plugin-node-resolve';
//import uglify from 'rollup-plugin-uglify';

export default {
  entry: 'src/app/main.js',
  format: 'iife',
  plugins: [ resolve() ],
  dest: 'dist/js/app.js',
  external: ['libs'],
  //sourceMap: true
};