//Praxyk JS Binding

//api urls
// var base_api_url= "http://api.praxyk.com:5000/v1/";
var base_api_url= "http://localhost:4001/v1/"  
var pod_api_url = base_api_url + "pod/";
var tlp_api_url = base_api_url + "tlp/";
var token_api_url = base_api_url + "tokens/";
var user_api_url = base_api_url + "users/";
var transaction_api_url = base_api_url + "transactions/";
var results_api_url = base_api_url + "results/";

function push_trans(transaction, token) {
    render_trans_card(transaction, function(html) {
        $("#new_trans_card").prepend(html);
        if(transaction.status == "active" || transaction.status == "new") {
            trans_spin(transaction.trans_id, token, "card");
        }
    })
}

function push_trans_button(transaction) {
    render_trans_button(transaction, function(html) {
        // console.log("#new_trans_button");
        $("#new_trans_button").append(html)
    })
}


function push_result_card(result, trans_id) {
    render_result_card(result, trans_id, function(html) {
        // console.log("#new_result_card");
        $("#new_result_card").append(html)
        // console.log(html)
    })
}


function render_trans_card(transaction, callback) {
    url = "/static/jstemplates/trans_card.html";
    return render_trans(transaction, url, callback);
}

function render_result_card(result, trans_id, callback) {
    url = "/static/jstemplates/result_card.html";
    return render_result(result, trans_id, url, callback);
}

function render_trans_button(transaction, callback) {
    url = "/static/jstemplates/trans_button.html";
    return render_trans(transaction, url, callback);
}

function render_trans(transaction, url, callback) {
    Handlebars.registerHelper('ifCond', function(v1, v2, options) {
          if(v1 === v2) {
                  return options.fn(this);
                    }
            return options.inverse(this);
    });
	Handlebars.registerHelper("tcard", function(id) {
		return "trans-card-" + (id);
	});
	Handlebars.registerHelper("tbutton", function(id) {
		return "trans-button-" + (id);
	});
	Handlebars.registerHelper("rcard", function(id) {
		return "result-card-" + (id);
	}); 
    $("#hidden-loader").load(url, function(result) {
            var template = Handlebars.compile(result);
		    transaction = date_prettify(transaction)
            var html    = template({transaction : transaction});
            callback(html)
            return html
    });
}

function render_result(result, trans_id, url, callback) {
    // console.log(result)
    Handlebars.registerHelper('ifCond', function(v1, v2, options) {
          if(v1 === v2) {
                  return options.fn(this);
			}
            return options.inverse(this);
    });
	Handlebars.registerHelper("rcard", function(id) {
		return "result-card-" + (id);
	}); 
    $("#hidden-loader").load(url, function(res) {
            var template = Handlebars.compile(res);
		    result = date_prettify(result)
            var html  = template({result : result, trans_id : trans_id });
            callback(html, result)
            return html
    });
}

function date_prettify(transaction)  {
	if(transaction && transaction.created_at) {
		transaction.created_at=new Date(transaction.created_at).toLocaleString();
	}
	if(transaction && transaction.finished_at) {
		transaction.finished_at=new Date(transaction.finished_at).toLocaleString();
	}
	return transaction;
}

function trans_spin(id, token, type, count) {
    if (typeof(count)==='undefined') count = 1;

    get_transaction(token, id, function(result) {
         // console.log(result)

         var json = result //$.parseJSON(result);
         // console.log("Spin Again")

        if(!json) {
            return false;
        }
        if(json.transaction.status == "finished" || json.transaction.status == "failed" ) {
            if(type=="button") {
                render_trans_button(json.transaction, function(html) { 
                    // console.log("#trans-button-"+id)
                    //$("#new_trans_card").prepend(html)

                    setTimeout(function (){
                        $("#trans-button-"+id).after(html);
                        $("#trans-button-"+id).remove()
                        // console.log("FINISHED!")
                    }, 100);
                })
            }else if(type=="card") {
                render_trans_card(json.transaction, function(html) { 
                    // console.log("#trans-card-"+id)
                    //$("#new_trans_card").prepend(html)

                    setTimeout(function (){
                        $("#trans-card-"+id).after(html);
                        $("#trans-card-"+id).remove()
                        // console.log("FINISHED!")
                    }, 100);
                })
            }
            return true;
        }

        setTimeout(function (){
            count = count+1;
            // console.log(count);
            return trans_spin(id, token, type, count++);
        }, Math.min(100+200*count, 5000));

    });

}



function results_spin(trans_id, active_results, token, type, count) {
    if (typeof(count)==='undefined') count = 1;
    if(active_results.length == 0) {
        update_result_pie(token, trans_id);
        return true;
    }

    get_results(token, trans_id, function(raw_results) {

        var json = raw_results //$.parseJSON(result);

        if(!json || !json.results) {
            return false;
        }
        var results = json.results;
        
        for(y = 0; y < results.length; y++) {
            // console.log("Iterating over Result :");
            if(active_results.indexOf(results[y].item_number) !== -1) {
                // console.log("Active Results Match Found");
                if(results[y].status === "finished" || results[y].status === "failed") {
                    x = y;
                    // console.log("Status finished/failed : ("+results[x].status+")");
                    // console.log("Active Results");
                    active_results.splice(active_results.indexOf(results[x].item_number), 1);
                    // console.log(active_results)
                    render_result_card(results[x], trans_id, function(html, result) { 
                        // console.log("#result-card-"+result.item_number)
                        // console.log("Changing Card!");
                        // console.log(result);
                        $("#result-card-"+result.item_number).replaceWith(html);
                        update_result_pie(token, trans_id);
                        // console.log("FINISHED!")
                    });
                }
            }
        }

        if(active_results.length == 0) {
            return true;
        }

        setTimeout(function (){
            count = count+1;
            // console.log(count);
            return results_spin(trans_id, active_results, token, type, count++);
        }, (active_results), Math.min(100+200*count, 5000));


    });
}


function make_request(service, token) {

    if(service != "pod") {
        return
    }else {
        var passed = true
        var files = $("#pod-input").prop("files");
        var name = $("#pod_name").val()
        var model = ""
        $('#pod_choices a').each(function () {
            if ($(this).hasClass('active')) {
                model = $(this).attr('val')
            }
        });

        if(!files || files.length <= 0) {
            passed=false
            $("#upload-form-group").addClass("has-error");
            $("#upload-form-group").removeClass("has-success");
            $("#upload_success").addClass("hidden");
            $("#upload_failure").removeClass("hidden");
            $("#upload_failure").text("Please Submit At Lease 1 File");
        }
        if(!name) {
            passed=false
            $("#upload_success").addClass("hidden");
            $("#upload_failure").removeClass("hidden");
            $("#upload_failure").text("Please Name Your Transaction");
            $("#main-form-group").removeClass("has-success");
            $("#main-form-group").addClass("has-error");
        }
        if(!model) {
            passed=false
            $("#upload_success").addClass("hidden");
            $("#upload_failure").removeClass("hidden");
            $("#upload_failure").text("Please Select a Model");
            $("#main-form-group").removeClass("has-success");
            $("#main-form-group").addClass("has-error");
        }   

        if(!passed) {
            return;
        }

        $("#main-form-group").removeClass("has-error");
        $("#upload-form-group").removeClass("has-error");

        do_pod(model, token, files, name, $("#upload_progress"), function(result) {
            var json = $.parseJSON(result);
            // console.log(json)
            if (json.transaction) {
                // $("#upload_success").removeClass("hidden");
                $("#upload_failure").addClass("hidden");
                $("#upload_failure").addClass("hidden");
                // $("#upload_success_btn").attr('href', '/dashboard/transaction/'+json.transaction.trans_id)
                push_trans_button(json.transaction)
                trans_spin(json.transaction.trans_id, token, "button")
                $('.fileupload').fileupload(clear);

            }else {
                // $("#upload_success").addClass("hidden");
                $("#upload_failure").removeClass("hidden");
                $("#upload_failure").text("There Was an Error With Your Request.");
            }

        })
    }

}


function do_pod(model, token,input, name, progress,callback){
	 
	//get the data ready
	var ocr_data = new FormData();
	for(var i=0;i<input.length;++i){
		var file = input[i];
		ocr_data.append("files",file,file.name);
	}
	
	//call api
	var result = api_call(pod_api_url+model+"/?token="+token+"&name="+name, "POST",ocr_data,null,progress,function(result) {
		callback(result)
    });
	
	
}

function get_api_token(username,password, callback){
   
   //get data ready
	var login_data = new Object();
	login_data.email = username;
	login_data.password = password;
	
	var json_data = JSON.stringify(login_data);

	//api call
	return api_call(token_api_url,"POST",json_data,"application/json",null,function(result) { 
        var login_json = $.parseJSON(result);
        if(login_json.code == 200) { 
            return callback(login_json);
        }
        else {
            return callback(null);
        }
    });
}

function register_user(first,last,email,password,callback){
   
   //get data ready
   var register_data = new Object();
   register_data.email = email;
   register_data.password = password;
   register_data.name = first + " " +last;
   
   var json_data = JSON.stringify(register_data);

   
   //api call
   return api_call(user_api_url,"POST",json_data,"application/json",null,function(result) {
       var json = $.parseJSON(result);
       
       if(json.code == 200) { return callback(true) }
       else { return callback(false) };
   });

}

function get_user_info(token,userid,callback){	
	//api call
	var url = user_api_url+userid.toString()+"?token="+token;
	return api_call(url,"GET",null,null,null,function(result) {
		var json = $.parseJSON(result);
       return callback(json);
   });
}

function get_transaction(token,id,callback){
	var url = transaction_api_url + id + "?token=" + token;
	return api_call(url, "GET",null,null,null,function(result) {
		var json = $.parseJSON(result);
		return callback(json);
	});
}

function get_all_transactions(token,userid,callback){
	var url = transaction_api_url + "?user_id=" + userid.toString() + "&pagination=False&token=" + token;
	return api_call(url, "GET",null,null,null,function(result) {
		var json = $.parseJSON(result);
		return callback(json);
	});
}

function get_results(token,trans_id,callback){
	var url = results_api_url + trans_id + "?pagination=False&token=" + token;
	return api_call(url, "GET",null,null,null,function(result) {
		var json = $.parseJSON(result);
		return callback(json);
	});
}

function get_all_transaction_results(token,trans_id,callback){
   var url = results_api_url + trans_id.toString() + "?pagination=False&token=" + token;
   return api_call(url,"GET",null,null,null,function(result){
      var json = $.parseJSON(result);
      return callback(json);
   });
}

function api_call(url,method,payload,content_type,prog,callback){
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function (){
		if(xhr.readyState==4 && xhr.status==200){
            callback(xhr.responseText);
		} 
	}
   if(prog != null){
   xhr.upload.onprogress = function(e) {
        var percentComplete = (e.loaded / e.total) * 100;
        prog.html(percentComplete.toString());
    };

    xhr.onload = function() {
        if (xhr.status == 200) {
            prog.html("Sucess! Upload completed");
        } else {
            prog.html("Error! Upload failed");
        }
    };
   }
	xhr.open(method,url,true);
	if(payload!=null){
		if(content_type!=null) xhr.setRequestHeader('Content-Type',content_type);
		xhr.send(payload);
	}else{
		xhr.send();
	}
}

function createCookie(name, value, expires, path, domain) {
  var cookie = name + "=" + escape(value) + ";";

  if (expires) {
    // If it's a date
    if(expires instanceof Date) {
      // If it isn't a valid date
      if (isNaN(expires.getTime()))
       expires = new Date();
    }
    else
      expires = new Date(new Date().getTime() + parseInt(expires) * 1000 * 60 * 60 * 24);

    cookie += "expires=" + expires.toGMTString() + ";";
  }

  if (path)
    cookie += "path=" + path + ";";
  if (domain)
    cookie += "domain=" + domain + ";";

  document.cookie = cookie;
}

function getCookie(name) {
  var regexp = new RegExp("(?:^" + name + "|;\s*"+ name + ")=(.*?)(?:;|$)", "g");
  var result = regexp.exec(document.cookie);
  return (result === null) ? null : result[1];
}

function deleteCookie(name, path, domain) {
  // If the cookie exists
  if (getCookie(name))
    createCookie(name, "", -1, path, domain);
}
