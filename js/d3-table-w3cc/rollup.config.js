import node from "rollup-plugin-node-resolve";
import cleanup from 'rollup-plugin-cleanup';
import json from 'rollup-plugin-json';

export default {
  plugins: [
	node({jsnext: true, browser: true, modulesOnly: true}),
	json(),
	cleanup()	
  ]
};