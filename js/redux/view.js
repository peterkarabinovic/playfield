var el = d3.select

var $input = el('input'),
    $button = el('button'),
    $todos = el('ul');

// UI
store.subscribe(function(){
    var todos = store.getState().todos;
    var $selection = $todos.selectAll('li.item').data(todos,_.property('id'));
    $selection.enter()
              .append('li')
                .classed('item',true)
                .text(_.property('text'))
                .each(function(){
                    var $li = el(this);
                    $li.append('button')
                       .text('.')
                       .on('click', function(it){ store.dispatch(toggleTodo(it.id)) });
                    $li.append('button')
                       .text('-')
                       .on('click', function(it){ 
                           store.dispatch(deleteTodo(it.id)) 
                        });    
                });
    $selection.exit().remove();
    $selection.classed('completed', _.property('completed'))
});


// 
$button.on('click', function(){
    var text = $input.node().value.trim()
    if(text)
        store.dispatch(addToDo(text))
});