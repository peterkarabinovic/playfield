

// import * as Redux from './lib/redux'
// import * as _ from './lib/lodash'


/****************************************** 
 * Actions
 *******************************************/
var unique_id = 0;
function addToDo(text){
    return { type: 'ADD_TODO', text: text, id: unique_id++ }
}

function toggleTodo(id){
    return { type: "TOGGLE_TODO", id: id}
}

function deleteTodo(id){
    return { type: "DELETE_TODO", id: id}
}


var FILTERS = ["show_all", "show_completed", "show_active"]

function setVisibility(filter){
    return { type: "SET_VISIBILITY", filter: filter}
}


/****************************************** 
 * Redusers   
 *******************************************/
 function todos(state, action)
 {
    state = state || [] 

    switch(action.type)
    {
        case "ADD_TODO":
            return state.concat( [ { text: action.text, completed: false, id: action.id }] );

        case "TOGGLE_TODO":
            return state.map( function(it){
                if(it.id === action.id){
                    return _.assign({},it,{ completed: !it.completed})
                }
                return it;
            });

        case "DELETE_TODO":
            return state.filter(function(it){
                return it.id !== action.id;
            });
        default:
            return state;
    }    
 }

 function visibility(state, action){
     state = state || "show_all";
     switch(action.type){
        case "SET_VISIBILITY":
            return action.filter;
        default:
            return state;
     }
 }

 var todoApp = Redux.combineReducers({
     visibility,
     todos
 });

/****************************************** 
 * Store   
 *******************************************/
var store = Redux.createStore(todoApp)




 
