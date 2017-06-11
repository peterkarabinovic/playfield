
import {startswith} from './utils.js'


var incorrect_file_type = 'Выберите SVG-файл.'
var invalid_file_content = 'SVG-файл с ошибками.'
var no_size_attributes = 'SVG-документ должен содержать атрибуты "width" и "height".'
var wrong_type_units = 'Атрибуты "width" и "height" SVG-документа\nдолжны задаваться в пикселях. "{width}" "{height}".'


export default function(el)
{

    var vm = new Vue({
        el: el,
        data: {
            error: '',
            file: null,
            raw_xml: null,
            svg_document: null,
            width_px: null,
            height_px: null,
            width_m: null,
            height_m: null
        },
        methods: {
            on_save: function(){
                this.$emit('NEW_SVG', {
                    raw_xml: this.raw_xml,
                    svg_document: this.svg_document,
                    width: this.width_px,
                    height: this.height_px,
                    width_m: this.width_m,
                    height_m: this.height_m
                });
            },
            on_change: function(e){
               var file = e.target.files[0] 
               vm.file = null;
               vm.error = null;
               if(!file)
                    return
               if(file.type !== 'image/svg+xml') {
                    vm.error = incorrect_file_type
                    return
                }
                var reader = new FileReader();
                reader.onloadend = function(xml){
                    var xml = reader.result
                    if(!xml || xml.length < 7) {
                        vm.error = incorrect_file_type = invalid_file_content
                        return
                    }
                    var parser = new DOMParser();    
                    var svg = parser.parseFromString(xml, "image/svg+xml").documentElement;
                    if( !svg ||
                        !svg.getAttribute ||
                        !startswith(svg.getAttribute('xmlns'), 'http://www.w3.org/2000/svg')) {
                            vm.error = incorrect_file_type = invalid_file_content;
                            return
                        }
                    if(!svg.height || !svg.width) {
                        vm.error = incorrect_file_type = no_size_attributes;
                        return;
                    }
                    var w = svg.width.baseVal
                    var h = svg.height.baseVal
                    var viewBox = null
                    if(svg.viewBox.baseVal && svg.viewBox.baseVal.width != 0) {
                        var vb = svg.viewBox.baseVal;
                        viewBox = [vb.x, vb.y, vb.width, vb.height].join(' ')
                        d3.select(svg).attr('viewBox', null)
                    }
                    else {
                        viewBox = '0 0 ' + Math.round(w.valueInSpecifiedUnits) + ' ' +  Math.round(h.valueInSpecifiedUnits);
                    }
                    
                    vm.raw_xml = xml;
                    vm.svg_document = svg;
                    vm.file = file.name;
                    vm.viewBox = viewBox;
                    vm.$emit('NEW_SVG', {
                        raw_xml: vm.raw_xml,
                        svg_document: vm.svg_document,
                        viewBox: vm.viewBox,
                        width_m: vm.width_m,
                        height_m: vm.height_m
                    });
                    
                }
                reader.readAsText(file)
                    
            }            
        }

    });

    vm.on = function(){ vm.$on.apply(vm, arguments)}
    return vm;
}