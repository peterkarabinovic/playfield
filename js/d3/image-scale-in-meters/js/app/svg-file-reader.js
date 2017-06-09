
import {startswith} from './utils.js'

var incorect_file_type = 'Выберите SVG-файл'
var invalid_file_content = 'SVG-файл с ошибками'
var no_size_attributes = 'SVG-документ должен содержать атрибуты "width" и "height"'
var wrong_type_units = 'Атрибуты SVG-документа "width" и "height" должны задаваться в пикселях.\n{width} {height}'

export default function SvgFileReader(input_id){
    var $el = d3.select(input_id)
    var dispatch = d3.dispatch("change", "error");

    $el.on('change', function(){
        var file = this.files[0]
        if(!file)
            return
        if(file.type !== 'image/svg+xml')
            return dispatch.call('error', this, incorect_file_type)
        
        var reader = new FileReader();
        reader.onloadend = function(xml){
            var xml = reader.result
            if(!xml || xml.length < 7)
                return dispatch.call('error', this, invalid_file_content)
            var parser = new DOMParser();    
            var svg = parser.parseFromString(xml, "image/svg+xml").documentElement;
            if( !svg ||
                !svg.getAttribute ||
                !startswith(svg.getAttribute('xmlns'), 'http://www.w3.org/2000/svg'))
                return dispatch.call('error', this, invalid_file_content)
            if(!svg.height || !svg.width)
                return dispatch.call('error', this, no_size_attributes)
            var w = svg.width.baseVal
            var h = svg.height.baseVal
            var unitTypes = [0,1,5]
            if(!_.contains(unitTypes,w.unitType) || !_.contains(unitTypes,h.unitType) ){
                var er = wrong_type_units.replace('{width}', w.valueAsString)
                                         .replace('{height}', h.valueAsString)
                return dispatch.call('error', this, er)
            }
            dispatch.call('change', this, {
                text: xml,
                svg_document: svg,
                width: w.value,
                height: h.value
            })
        }
        reader.readAsText(file)
    })  
    
    return dispatch
}