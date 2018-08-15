
$(document).ready(function(){
    $("#btn_send").click(function(event){
        content = $("#txt_content").val();
        if (content == "") {
            alert("Content can not be empty!");
            return;
        }
        $.ajax({url: "remote_server/send_content", type: "POST", dataType: "json", data: {"txt": content}})
            .done(function(data){
                $("#txt_content").val("");
            });
    });

});


