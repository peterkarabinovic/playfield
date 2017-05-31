import Vue from 'vue'
import {scaleLinear} from 'd3-scale'


var x = scaleLinear()
    .domain([0, 10])
    .range([0, 960]);

var data = {a:1}
var vm = new Vue({
    el: '#app',
    data: data
})

console.log(data.a == vm.a)

data.a = 3

console.log(vm.a)

window.foo = function(y)
{
    data.a = x(y)
}