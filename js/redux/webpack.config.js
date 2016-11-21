var webpack = require("webpack");
module.exports = {
    entry: "./app.js",
    output: {
        path: __dirname,
        filename: "app_lib.js"
    },
    plugins: [
	new webpack.optimize.UglifyJsPlugin()	
    ]
};