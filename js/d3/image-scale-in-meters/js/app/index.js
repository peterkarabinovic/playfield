// import SvgFileReader from './svg-file-reader.js'


// var svg_reader = SvgFileReader('#file')

// svg_reader.on('error', function(er){
//     alert(er)
// });

// svg_reader.on('change', function(event){
//     var $map = d3.select('#map')
//     $map.selectAll("*").remove();
//     $map.node().appendChild(event.svg_document)
// })

import FileWidget from './file-component'

var file_widget = FileWidget('#svg-selector')