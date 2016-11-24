
(function(){

    var $body = document.getElementById('mithril');
    var $list_el = $body.getElementsByClassName('todolist')[0]
    var $filters_el = $body.getElementsByClassName('visibility')[0]

    function filterByVisibility(visibility){
        return function(todo){
            switch(visibility) {
                case "show_all": return true;
                case "show_completed": return todo.completed;
                case "show_active": return !todo.completed;
                }
            }
    }

    var $filters = function(){
         var visibility = store.getState().visibility;
         return FILTERS.map(function(it){
             return m('li', {class: _.isEqual(it,visibility) ? 'disable-link': '' }, [
                 m('a', {href:'#', onclick: function(){
                     store.dispatch( setVisibility(it) );
                 }}, it)
             ]);
         });   
    };
    

    var $list = {
        todos: function(){
            var todos = store.getState().todos;
            var visibility = store.getState().visibility;
            return todos.filter(filterByVisibility(visibility));
        },

        view: function(){
            return this.todos().map(function(it){
                return m('li', {class: it.completed ? 'completed' : ''}, it.text, [
                    m("input[type=checkbox]", {checked: it.completed, onclick: function(){
                        store.dispatch(toggleTodo(it.id));
                    }}),
                    m("a", {href:"#", onclick: function(){
                        store.dispatch(deleteTodo(it.id)) 
                    }}, "delete")
                ])
            });
        }
    }

    store.subscribe(function(){
        m.render( $list_el, $list.view() )
        m.render( $filters_el, $filters() )
    });

    m.render( $filters_el, $filters() )

})();


