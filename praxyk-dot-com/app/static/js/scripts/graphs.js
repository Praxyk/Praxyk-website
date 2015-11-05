// JavaScript Document
function transaction_status_pie(state_counts, state_names) {
    var data = [{
      values: state_counts,
      labels: state_names,
      type: 'pie'
    }];

    var layout = {
    margin : {l:30, r:30, t:20, b:20},
    height : 200,
    pad : 50,
    showlegend : false
    };


    Plotly.newPlot('tester', data, layout, {showLink : false});
}

function transaction_status_bar(date_counts, dates) {
    var data = [{
      y: date_counts,
      x: dates,
      type: 'bar'
    }];

    var layout = {
    margin : {l:30, r:30, t:20, b:20},
    height : 200,
    pad : 50,
    xaxis:  {type:"date"},
    showlegend : false
    };


    Plotly.newPlot('date-counts', data, layout, {showLink : false});
}
