function find_element_rec(fn, list, n) =
    fn(list[n]) ?
        list[n] :
        n+1 >= len(list) ?
            undef :
            find_element_rec(fn, list, n+1)
;

/* Find an element in list for which fn yields true */
function find_element(fn, list) =
    find_element_rec(fn, list, 0)
;

function lookup_dict_rec(key, dict, n) =
    dict[n][0] == key ?
        dict[n][1] :
        n+1 >= len(dict) ?
            undef :
            lookup_dict_rec(key, dict, n+1)
;

// Should implement using lambdas and find_element
// But that requires OpenSCAD 2021.01
/* Return value associated with key in dict */
function lookup_dict(key, dict) =
    lookup_dict_rec(key, dict, 0)
;