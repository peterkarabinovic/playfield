import d3select from 'd3-selection/src/select'
import d3dispatch from 'd3-dispatch/src/dispatch'
import {event as d3event} from 'd3-selection/src/selection/on'
import {default as d3selectAll} from 'd3-selection/src/selectAll'
import {default as d3scaleLinear}  from 'd3-scale/src/linear.js' 
import {default as d3drag} from 'd3-drag/src/drag'


import _ from 'underscore'


function styles(selection, map){
    for (var name in map) selection.style(name, map[name]);
}

export default function d3Grid(div_id, options)
{
    var min = Math.min,
        max = Math.max,
        $div = d3select(div_id);
    var $tableDiv = $div.append('div');
    $tableDiv.style('overflow-x', 'auto')
    var $table = $tableDiv.append('table'),
        $thead = $table.append('thead').style('cursor','pointer'),
        $tbody = $table.append('tbody'),
        _columns = [],
        _id = _ => _,
        _scrollPos = 0,
        _startIndex = 0,
        _data = [],
        $scroll = d3selectAll([]),
        sortColumn = '',
        desc = true,
        _columnClick = function(column){
            desc = sortColumn === column && !desc;
            sortColumn = column;
            _data.sort(function(a,b){
                a = a[column];
                b = b[column];
                if(a > b) return desc ? -1 : 1;
                if(a < b) return desc ? 1 : -1;
                return 0;
            });
            t(_data);
            $thead.selectAll('span').remove();
            $thead.selectAll('th')
                    .filter( d => d == sortColumn)
                        .append('span').text( () => desc ? '↑' : '↓')
                        .style('padding-left', '7px')

        },
        _render = function($tr, start){
            _startIndex = start;
            var $td = $tr.selectAll('td').data(function(index){
                index = index + start;
                if(_data.length > index) return _.values(_data[index]); 
                else return [];
            })
            $td.exit().remove();
            $td.enter().append('td').merge($td).text(_id);
        }

    var dispatch = d3dispatch('click','contextmenu','mouseenter', 'mouseleave');
    
    function eventHandlers($tr)
    {
        var handler = event_type => {
            return function(index){
                var td = d3event.target;
                var col = td.cellIndex;            
                var tr = this;
                dispatch.call(event_type, this, {
                    row: index + _startIndex,
                    column: _columns[col],
                    data: _data[index + _startIndex],
                    trElement: tr,
                    tdElement: td,
                    originalEvent: d3event
                }) 
            }
        };

        $tr.on('click', handler('click'));
        $tr.on('contextmenu', handler('contextmenu'));
        $tr.on('mouseenter', handler('mouseenter'));
        $tr.on('mouseleave', handler('mouseleave'));
    }
        
    function t(data)
    {
        // t.header();
        _data = data;
        _scrollPos = 0;
        _startIndex = 0;
        $scroll.remove();
        
        var size = Math.floor(($div.node().clientHeight - $thead.node().clientHeight) / $thead.node().clientHeight);
        var $tr = $tbody.selectAll('tr').data(_.range(min(size, data.length)));
        $tr.exit().remove();
        $tr = $tr.enter().append('tr').call(eventHandlers);
        $tr = $tr.merge($tr)
      
        
        tuneSizes(data);
        

        function refresh(start)
        {
            _render($tbody.selectAll('tr'), start);
        }
        refresh(0);

        var npages = data.length / size;
        if(npages > 1)
        {
            var w = 10;
            $div.style('padding-right',w+'px');
            var box = $table.node().getBoundingClientRect();
            $scroll = $div.selectAll('div.scroll').data([0])
            $scroll = $scroll.enter().append('div').classed('scroll',true).merge($scroll);
            var $scrollthumb = $scroll.selectAll('div').data([0]);
            $scrollthumb = $scrollthumb.enter().append('div').merge($scrollthumb);

            styles($scroll, {
                position: 'absolute',
                top: '0px',
                right: '0px',
                width: w+'px',
                height: box.height + 'px',
                cursor: 'pointer'
            }); 
            
            

            var scrollthumb_h = Math.max(box.height / npages, 25); 
            var scale = d3scaleLinear().domain([0, box.height-scrollthumb_h]).rangeRound([0, data.length-size]);           

            styles($scrollthumb, {
                position: 'absolute',
                width: w+'px',
                top: '0px',
                height: scrollthumb_h + 'px',
                'border-radius': '1px',
                'background-color': '#808080'
            });

            function moveAndUpdate(dy){
                var pos = _scrollPos + dy;
                pos = Math.max(pos,0);
                pos = Math.min(pos,box.height-scrollthumb_h);
                if(_scrollPos !== pos)  {
                    $scrollthumb.style('top', pos + "px");
                    refresh(scale(pos));
                    _scrollPos = pos;
                }
            }

            $scrollthumb.call(d3drag().on('drag', function(){
                moveAndUpdate(d3event.dy);
            }));


            $scroll.on('click', function(){
                var sign = d3event.clientY > $scrollthumb.node().getBoundingClientRect().top ? 1 : -1;
                var step = scale.invert(Math.round(size - 1));
                moveAndUpdate(sign * step);
                return false;
            });

            $tbody.on('wheel', function(){
                var sign = d3event.deltaY < 0 ? -1 : 1;
                var step = scale.invert(Math.round(size / 10 + 0.5));
                moveAndUpdate(sign * step);
            });
        }
    };

    t.header = function(columns){
        _columns = columns.slice(0);
        var $tr = $thead.selectAll('tr').data([0]);
        $tr = $tr.enter().append('tr').merge($tr);
        var $th = $tr.selectAll('th').data(_columns);
        $th.exit().remove();
        $th.enter()
            .append('th').on('click',_columnClick)
            .merge($th)
                .text(_id);
        
        

        return t;
    };

    t.$table = function(){
        return $table; 
    }

    t.$thead = function(){
        return $thead; 
    }
    t.$tbody = function(){
        return $tbody; 
    }

    t.renderRow = function(fn){
        return (_render = fn, t);
    };
    
    t.data = function(){
        return _data;
    };

    function tuneSizes(data)
    {
        var $th = $thead.select('th').node(),
            styles = getComputedStyle($th),
            padding = parseFloat(styles.paddingLeft) + parseFloat(styles.paddingRight);

        var canvas = tuneSizes.canvas || (tuneSizes.canvas = document.createElement("canvas"));
        var context = canvas.getContext("2d");
        context.font = styles.font;
        var metrics = context.measureText('w');

        var chars = _.map(_columns,function(it){return min(70,it.length)});
        for(var i=0, len=min(500, data.length); i<len; i++){
            var index = _.random(data.length-1);
            var d = data[index];
            _.each(_columns, function(k,i){
                var l = min(70,(""+d[k]).length);
                if(chars[i] < l ) chars[i] = l;
            })
        }
        var w = metrics.width;
        var table_w = 0;
        $thead.selectAll('th').each(function(d,i){
            var width = chars[i] * w ;
            table_w += chars[i] * w ;
            d3select(this).style('width', width +'px')
        });
        $table.style('width', table_w + 'px');
    }
    t = _.extend(t,dispatch);
    return t;      
};

export function gridActions(d3grid, decorator_id)
{
    var $decorator = d3select(decorator_id);
    d3grid.on('mouseenter ', (e) => {
        var r = e.trElement.getBoundingClientRect();
        $decorator.style('top', r.top + 'px')
        $decorator.style('left', r.right + 'px')
        $decorator.style('display', 'block')
    });
    
   
    d3grid.on('mouseleave', (e) => {
        if(e.originalEvent.relatedTarget !== $decorator.node())
        $decorator.style('display', 'none')
    })
    $decorator.on('mouseleave', () => $decorator.style('display', 'none'))
}