var date = new Date();
var year = date.getFullYear();
var month = date.getMonth();
var day = date.getDate();
// document.getElementById("current_date").innerHTML = month + "/" + day + "/" + year;
$('#preview_title').html(year + "년 " + month + "월 " + day + "일 뉴스클리핑");


$('.keyword-tab').click(function(){
    console.log("here");
    console.log(this);
});