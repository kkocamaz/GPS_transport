const OSRM = require("osrm");
// const fs = require('fs');
var osrm = new OSRM("turkey-latest.osrm");

// console.log(process.argv[2]);

// let rawdata = process.argv[2];
// let options = JSON.parse(rawdata);
// console.log("here")


var input_array = "";
process.stdin.setEncoding('utf-8')
process.stdout.setEncoding('utf-8')

// 'readable' may be triggered multiple times as data is buffered in
process.stdin.on('readable', () => {
  let chunk;
  //console.log('Stream is readable (new data received in buffer)');
  // Use a loop to make sure we read all currently available data
  while (null !== (chunk = process.stdin.read())) {
    input_array += chunk;
  }
});
process.stdin.on('end', () => {
  //const content = process.stdin.read()
  const content = input_array;
  if (!!content) {
    // console.log(content);
    
    let options = JSON.parse(content);
    options.annotations = true;
    options.gaps = "split";
    options.tidy = false;
    options.geometries = "geojson";
    options.overview = 'false';
    // options.algorithm = 'CoreCH';
    // console.log(options);
    generate_hints = false;
    osrm.match(options, function (err, response) {
      // console.log("here");
      if (err) {
        
        console.log(JSON.stringify({
          status: false,
          err: JSON.stringify(err)
        }));

        return;
      }
	response["confidence"] = response.matchings.map(x => (x !== null && x !== undefined ?x.confidence: null));
	response["matchings_index"] = response.tracepoints.map(x => (x !== null && x !== undefined ?x.matchings_index: null));
      response.tracepoints = response.tracepoints.map(x => (x !== null && x !== undefined ? x.location: null));
      response.matchings = response.matchings.map(ms => ms.legs.map(x => (x !== null && x !== undefined ? x.annotation: null)).map(y => (y !== null && y !== undefined ? y.nodes: null)));
      
      console.log(JSON.stringify({
        status: true,
        response: response
      }));
//      const object = { a: 5, b: 6, c: 7  };
      //const picked = (({ tracepoints}) => ({ tracepoints}))(response);
      //console.log(Object.keys(response.tracepoints));
      //console.log(typeof response.tracepoints);
      //console.log(response.tracepoints); // array of Waypoint objects
      //console.log(response.matchings); // array of Route objects
    });
  }
})
