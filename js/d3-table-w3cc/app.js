import _ from 'underscore'
import {default as d3grid, rowDecorator} from './d3-grid'
import d3select from 'd3-selection/src/select'

var fields = ['m1', 'p2', 'p3', 'p4', 'чернозем?'];

function generate(n) {
    return _.range(n).map(function (i) {
        return _.object(_.map(fields, function (f) { return [f, f + '_' + i] }))
    });
}

var size = 20;

var table = d3grid('#table', {actions:true});
table.header(fields);
table.$table().classed('w3-table-all w3-small w3-hoverable', true)
table.$tbody().style('cursor', 'pointer')
table(generate(10000))

rowDecorator(table, '#close')
var $close = d3select('#close')

$close.on('click', () => {
    table(generate(10000))
    $close.style('display', 'none')
})

window.table = table;
