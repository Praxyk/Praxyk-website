// JavaScript Document

function evaluate_service(){
	$("#error_message").removeClass("alert alert-error");
	$("#error_message").html("");
   
	var token = sessionStorage.getItem("token");	
	var service = $("#pod_service").val();
	
	if(service == "false"){
		print_error("Please choose a valid service");
	}else{
		switch(service){
			case "ocr":
				var files = $("#pod_ocr_input").prop("files");
                $("#pod_ocrinput").val('');
                name = $("#pod_ocr_input").val()
				get_text_from_image(token,files,name, $("#upload_progress"),function(result){
					get_trans();
				});
				break;
		}
	}
}

function make_request(service, model, token) {

    if(service != "pod") {
        return
    }else {
        switch(model) {
            case "ocr" :
                var files = $("#pod_ocr_input").prop("files");
            break;
        }
    }

}

