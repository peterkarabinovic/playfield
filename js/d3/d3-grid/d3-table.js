
d3.table = function($div, rowHeight)
{
    var min = Math.min,
        max = Math.max;
    rowHeight = rowHeight || 20;
    var $tableDiv = $div.append('div');
    $tableDiv.style('overflow-x', 'auto')
    var $table = $tableDiv.append('table'),
        $thead = $table.append('thead'),
        $tbody = $table.append('tbody'),
        _columns = [],
        _id = function(_) {return _;},
        _scrollPos = 0,
        _startIndex = 0,
        _data = [],
        $scroll = d3.selectAll([]),
        _rowClick = function(row){},
        prevSort = '',
        desc = true,
        _columnClick = function(column){
            desc = prevSort === column && !desc;
            prevSort = column;
            _data.sort(function(a,b){
                a = a[column];
                b = b[column];
                if(a > b) return desc ? -1 : 1;
                if(a < b) return desc ? 1 : -1;
                return 0;
            });
            t(_data);
        },
        _render = function($tr, start){
            var $td = $tr.selectAll('td').data(function(index){
                index = index + start;
                if(_data.length > index) return _.values(_data[index]); 
                else return [];
            })
            $td.enter().append('td');
            $td.exit().remove();
            $td.text(_id);
        }


    function t(data)
    {
        t.header();
        _data = data;
        _scrollPos = 0;
        _startIndex = 0;
        $scroll.remove();
        
        var size = Math.floor(($div.node().clientHeight - $thead.node().clientHeight) / rowHeight);
        var $tr = $tbody.selectAll('tr').data(_.range(min(size, data.length)));
        $tr.enter().append('tr').on('click',function(index){  _rowClick(index+_startIndex) });
        $tr.exit().remove();

        
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
            $scroll = $div.selectAll('div.scroll').data([0]).enter().append('div').classed('scroll',true);
            var  $scrollthumb = $scroll.selectAll('div').data([0]).enter().append('div');

            $scroll.style({
                position: 'absolute',
                top: '0px',
                right: '0px',
                width: w+'px',
                height: box.height + 'px',
                cursor: 'pointer'
            });    

            var scrollthumb_h = Math.max(box.height / npages, 25); 
            var scale = d3.scale.linear().domain([0,box.height-scrollthumb_h]).rangeRound([0,data.length-size]);           

            $scrollthumb.style({
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

            $scrollthumb.call(d3.behavior.drag().on('drag', function(){
                moveAndUpdate(d3.event.dy);
            }));


            $scroll.on('click', function(){
                var sign = d3.event.clientY > $scrollthumb.node().getBoundingClientRect().top ? 1 : -1;
                var step = scale.invert(Math.round(size - 1));
                moveAndUpdate(sign * step);
                return false;
            });

            $tbody.on('wheel', function(){
                var sign = d3.event.deltaY < 0 ? -1 : 1;
                var step = scale.invert(Math.round(size / 10 + 0.5));
                moveAndUpdate(sign * step);
            });
        }
    };

    t.header = function(columns){
        _columns = columns || _columns;
        if( !_columns) return;

        var $tr = $thead.selectAll('tr').data([0]);
                  $tr.enter().append('tr');
        var $th = $tr.selectAll('th').data(_columns);
        $th.enter().append('th').on('click',_columnClick);
        $th.exit().remove();
        $th.text(_id);

        return t;
    };



    t.classed = function(clazz){
        $table.classed(clazz, true);
    };

    t.onRowClick = function(fn){
        return (_rowClick = fn, t);
    };

    t.onColumnClick = function(fn){
        return (_columnClick = fn, t);
    };

    t.renderRow = function(fn){
        return (_render = fn, t);
    };
    
    t.data = function(){
        return data;
    };

    function tuneSizes(data)
    {
        var canvas = tuneSizes.canvas || (tuneSizes.canvas = document.createElement("canvas"));
        var context = canvas.getContext("2d");
        var metrics = context.measureText('m');
        

        var chars = _.map(_columns,function(it){return min(70,it.length)});
        for(var i=0, len=min(500, data.length); i<len; i++){
            var d = data[_.random(0,data.length)];
            _.each(_columns, function(k,i){
                var l = min(70,(""+d[k]).length);
                if(chars[i] < l ) chars[i] = l;
            })
        }
        var w = metrics.width;
        var table_w = 0;
        $thead.selectAll('th').each(function(d,i){
            table_w += chars[i] * w;
            d3.select(this).style('width', chars[i] * w +'px')
        });
        $table.style('width', table_w + 'px');
  }
    
    return t;      
};