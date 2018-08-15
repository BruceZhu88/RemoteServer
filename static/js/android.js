
$(document).ready(function(){

    $("#screencap").click(function(event){
    	cmd = {"cmd": $(this).attr('id')};
        $.ajax({url: "android/adb", type: "POST", dataType: "json", data: cmd})
            .done(function(data){
            	
        	});
    });


});
