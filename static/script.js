const API_KEY = config.API_KEY;
const list = document.getElementById("autocompleteList");
const div = document.getElementById("autocomplete");
const input = document.getElementById("search")
input.addEventListener('input', wait);      
var delayTimer;

function wait(e) {
    
    if (!e.target.value && !document.getElementById('autocomplete').classList.contains('hidden')) {
        document.getElementById('autocomplete').classList.add('hidden');
    }
    clearTimeout(delayTimer);
    delayTimer = setTimeout( function () {
        if (e.target.value) {
            div.classList.remove('hidden');
        }
        list.innerHTML = '';
            

        let url = ''.concat('https://api.themoviedb.org/3/search/multi?api_key=', API_KEY, '&query=', e.target.value);
        fetch(url).then(result=>result.json()).then((data)=>{
            let results = data["results"];
            var path = window.location.pathname;
            var list_id = path.substring(path.lastIndexOf('/') + 1);
            
            for (let i = 0; i < results.length; i++) {
                if (results[i].media_type == "tv" || results[i].media_type == "movie") {

                    var entry = document.createElement('li');
                        
                    if (results[i].media_type == "tv") {
                        entry.appendChild(document.createTextNode(`${results[i].name} (${(results[i].first_air_date).substring(0, 4)})`));    
                        list.appendChild(entry);
                        var entry_type = 1;

                        entry.setAttribute('onclick', `addEntry('${results[i].id}', ${entry_type}, '${list_id}')`);

                    }
                    if (results[i].media_type == "movie") {
                        entry.appendChild(document.createTextNode(`${results[i].title} (${(results[i].release_date).substring(0, 4)})`));    
                        list.appendChild(entry);
                        var entry_type = 0;
                        entry.setAttribute('onclick', `addEntry('${results[i].id}', ${entry_type}, '${list_id}')`);
                    }
                    
                    
                }
            }
        });
    }, 400);
}
function addEntry(id, entry_type, list_id) {
    var entry = {
        id: id,
        list_id: list_id,
        entry_type: entry_type
    };

    
    fetch(`${window.origin}/add`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function (response) {
        if (response.status !== 200) {
            console.log(`Error: ${response.status}`);
            return ;
        }                       
        response.json().then(function (data){
            console.log(data);
        });
        location.reload();
    });
}

function addFriend(id, username) {
    var entry = {
        id: id,
        username: username
    };

    fetch(`${window.origin}/addFriend`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function (response) {
        if (response.status !== 200) {
            console.log(`Error: ${response.status}`);
            return ;
        }                       
        response.json().then(function (data){
            console.log(data);
        });
        var btn = document.getElementById(`${id}`);
        btn.innerHTML = "Remove Friend";
        //location.reload();
    });
}

function removeFriend(id, username) {
    var entry = {
        id: id,
        username: username
    };

    fetch(`${window.origin}/removeFriend`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function (response) {
        if (response.status !== 200) {
            console.log(`Error: ${response.status}`);
            return ;
        }                       
        response.json().then(function (data){
            console.log(data);
        });
        var btn = document.getElementById(`${id}`);
        btn.innerHTML = "Add Friend";
        //location.reload();
    });
}

function addOrRemove(id, name) {
    const button = document.getElementById(`${id}`);
    if (button.innerHTML == "Add Friend") {
        addFriend(id, name);
    }
    if (button.innerHTML == "Remove Friend") {
        removeFriend(id, name);
    }
}



function deleteItem(id) {
    
    var url = window.location.pathname;
    var list_id = url.substring(url.lastIndexOf('/') + 1);
    var entry = {
        id: parseInt(id),
        list_id: list_id
    }
    console.log(entry);
    fetch(`${window.origin}/delete`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }).then( function (response) {
        if (response.status != 200) {
            console.log(`Error: ${response.status}`);
            return ;
        }
        response.json().then(function (data) {
            console.log(data);
        });
    });
    location.reload();
}


function deleteList(id) {
    var entry = {
        id: id
    };
    
    fetch(`${window.origin}/deleteList`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(entry),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function (response) {
        if (response.status !== 200) {
            console.log(`Error: ${response.status}`);
            return ;
        }                       
        response.json().then(function (data){
            console.log(data);
        });
        window.location.replace(`${window.origin}`);
    });
}