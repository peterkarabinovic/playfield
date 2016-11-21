

// import * as Redux from './lib/redux'
// import * as _ from './lib/lodash'


/****************************************** 
 * Actions
 *******************************************/
function addToDo(text){
    return { type: 'ADD_TODO', text: text }
}

function toggleTodo(index){
    return { type: "TOGGLE_TODO", index: index}
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
            return state.concat( [ { text: action.text, completed: false }] );

        case "TOGGLE_TODO":
            return state.map( function(it, index){
                if(index === action.index){
                    return _.assign({},it,{ completed: !it.completed})
                }
                return it;
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

export default store;  



 
