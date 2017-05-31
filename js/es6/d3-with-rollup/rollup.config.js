import resolve from 'rollup-plugin-node-resolve';


export default {
  entry: 'src/main.js',
  format: 'iife',
  dest: 'dist/bundle.js',
  plugins: [ resolve() ]
};