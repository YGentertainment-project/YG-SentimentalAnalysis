var date = new Date();
var year = date.getFullYear();
var month = date.getMonth();
var day = date.getDate();
// document.getElementById("current_date").innerHTML = month + "/" + day + "/" + year;
$('#preview_title').html(year + "년 " + month + "월 " + day + "일 뉴스클리핑");


$("#tab1").click(function(){
    console.log("here");
});

$('input[name=tabmenu]').click(function(){
    console.log("here");
});