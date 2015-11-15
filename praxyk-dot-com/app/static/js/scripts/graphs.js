// JavaScript Document

function status_bar(date_counts, dates, div) {
    var data = [{
      y: date_counts,
      x: dates,
      type: 'bar'
    }];

    var layout = {
    margin : {l:30, r:30, t:20, b:20},
    height : 200,
    pad : 50,
    showlegend : false
    };


    Plotly.newPlot(div, data, layout, {showLink : false});
}


function status_pie(state_counts, state_names, div) {

    console.log("Status Pie Being Called");
    console.log(state_counts);
    console.log(state_names);
    colors = ["#1F5C1C", "#37474f", "#37474f", "#7D2529", "#7D2529"];
    var data = [{
      values: state_counts,
      labels: state_names,
      marker :  {
        colors: colors,
      },
      type: 'pie'
    }];

    var layout = {
    margin : {l:30, r:30, t:20, b:20},
    height : 200,
    pad : 50,
    autosize : "initial",
    showlegend : false
    };


    Plotly.newPlot(div, data, layout, {showLink : false});
}


function update_result_pie(token, trans_id) {
	
	console.log("UPDATING RESULT PIE");

	return get_results(token, trans_id, function(raw_results) {
        var json = raw_results //$.parseJSON(result);
        console.log("RAW Results : ");
        console.log(json);

        if(!json || !json.results) {
            return false;
        }
        var results = json.results;
        
		var state_dict = {};
		var state_names = ["finished", "active", "new", "failed", "canceled"];
		var state_vals = [];
        for(y = 0; y < results.length; y++) {
			if(!state_dict[results[y].status]) {
				state_dict[results[y].status] = 1;
			}
			else {
				state_dict[results[y].status] += 1;
			}
		}
        console.log(state_dict);

        for(x = 0; x < state_names.length; x++) {
            if(state_dict[state_names[x]]) {
                state_vals.push(state_dict[state_names[x]]);
            }
            else {
                state_vals.push(0);
            }
        }
        console.log(state_names);
        console.log(state_vals);

		status_pie(state_vals, state_names, 'results-status-pie');

	});

}
