# Bar chart race — the most populous cities in the world

https://observablehq.com/@johnburnmurdoch/bar-chart-race-the-most-populous-cities-in-the-world@1205

View this notebook in your browser by running a web server in this folder. For
example:

~~~sh
python -m http.server
~~~

Or, use the [Observable Runtime](https://github.com/observablehq/runtime) to
import this module directly into your application. To npm install:

~~~sh
npm install @observablehq/runtime@4
npm install https://api.observablehq.com/@johnburnmurdoch/bar-chart-race-the-most-populous-cities-in-the-world.tgz?v=3
~~~

Then, import your notebook and the runtime as:

~~~js
import {Runtime, Inspector} from "@observablehq/runtime";
import define from "@johnburnmurdoch/bar-chart-race-the-most-populous-cities-in-the-world";
~~~

To log the value of the cell named “foo”:

~~~js
const runtime = new Runtime();
const main = runtime.module(define);
main.value("foo").then(value => console.log(value));
~~~
