(function(){

var el = d3.select

var $input = el('#d3 input'),
    $button = el('#d3 button'),
    $todos = el('#d3 ul.todolist'),
    $visibility = el('#d3 ul.visibility')


// UI
function filterByVisibility(visibility){
    return function(todo){
        switch(visibility) {
            case "show_all": return true;
            case "show_completed": return todo.completed;
            case "show_active": return !todo.completed;
        }
    }
}


store.subscribe(function(){
    var todos = store.getState().todos;
    var visibility = store.getState().visibility;
    todos = todos.filter(filterByVisibility(visibility));
    var $selection = $todos.selectAll('li.item').data(todos,_.property('id'));
    $selection.exit().remove();
    $selection.enter()
                .append('li')
                .classed('item',true)
                .text(_.property('text'))
                .each(function(){
                    var $li = el(this);
                    $li.append('input').attr('type','checkbox')
                    .on('click', function(it){ 
                        store.dispatch(toggleTodo(it.id)) 
                        });
                    $li.append('a').text('delete').attr('href','#')
                    .on('click', function(it){ 
                        store.dispatch(deleteTodo(it.id)) 
                        });    
                })
            .merge($selection)
                .classed('completed', _.property('completed'))
                .select('input')
                    .property('checked',_.property('completed'));
});

$visibility.selectAll('li')
            .data(FILTERS)
            .enter()
                .append('li')
                .append('a')
                .attr('href','#')
                .text(_.identity)
                .on('click', function(it) { 
                    store.dispatch(setVisibility(it) );
                });


store.subscribe(function(){
    var visibility = store.getState().visibility;
    $visibility.selectAll('li')
                .data(FILTERS)
                .classed('disable-link', function(it){
                    return _.isEqual(it, visibility);
                });
});

// 
$button.on('click', function(){
    var text = $input.node().value.trim()
    if(text) {
        store.dispatch(addToDo(text));
        $input.node().value = '';
    }
});

})();