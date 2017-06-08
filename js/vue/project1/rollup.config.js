var node = require('rollup-plugin-node-resolve')
var alias = require('rollup-plugin-alias')
var uglify = require('rollup-plugin-uglify');
var replace = require('rollup-plugin-replace')
export default {
  entry: 'src/main.js',
  format: 'iife',
  dest: 'dist/main.js', // equivalent to --output,
  plugins: [   
    uglify(), 
    replace({'process.env.NODE_ENV': JSON.stringify('production')}), 
    alias({'vue': 'node_modules\\vue\\dist\\vue.esm.js'}), 
    node()
  ]
};