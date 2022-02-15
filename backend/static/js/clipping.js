$(".border-btn").click(function(){
    console.log("here");
    if(!$('#group_content').hasClass("show")){
     $('#group_content').removeClass("hide")
     $('#group_content').addClass("show")
    } else{
     $('#group_content').removeClass("show")
     $('#group_content').addClass("hide")
    }
 });
 