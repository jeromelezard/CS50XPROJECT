# LISTY
#### Video Demo:  <https://www.youtube.com/watch?v=WhtRdWVcUz4>
#### Description:
I have created a website that accesses an API of all movies and TV shows ever made, and allows you to create custom lists containing these TV shows or Movies for you to share with your friends. It can access data on all TV shows and Movies thanks to themoviedb.org's public API which anyone can be granted access to use, provided you state them as the source of the data on all pages as I have done.

The website is made in Python using the microframework Flask, as well as vanilla Javascript and Jinja2 for HTML templating. While the project began with using Bootstrap, eventually the styling ended up being designed with standard CSS, with only a few bootstrap elements across the site. Sqlite3 is used for the database, which is comprised of 4 relational tables.

The use of this API is the backbone of the project, as it has all the relevant movie information needed including poster pictures to use. However the API also caused some problems that had to be navigated. For example, I had to be careful not to call the API too many times, since not only is it time consuming for the user of the website, but the API's rate limit will eventually not allow the thousands of calls. However an autocompleting search bar to add the movies/tv shows to the list meant calling the API with every key stroke which is far too many times. Therefore there is a function in script.js that makes sure the API is only called a certain amount of time after the user has stopped typing, allowing for more efficient run times and fewer API calls.

The friends page allows you to keep up with all the lists that anyone on the site. You can easily lookup any user and see their lists and entries. Adding the user adds them to your friends page which allows for quick and easy access to all your friends lists.

Accessing and changing elements of the database without having to refresh the page was also a crucial part for the user experience. This was done by using the asychronous fetch function in javascript, which allows an app route from the Python back end be run without having to refresh the page. This is how friends can be added and removed without the page refreshing.

