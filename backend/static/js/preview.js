var date = new Date();
var year = date.getFullYear();
var month = date.getMonth();
var day = date.getDate();
// document.getElementById("current_date").innerHTML = month + "/" + day + "/" + year;
$('#preview_title').html(year + "년 " + month + "월 " + day + "일 뉴스클리핑");


//탭바 누를 때마다 아래 바뀌도록 설정
$('.keyword-tab').click(function(){
    $(this.childNodes[1]).prop('checked', true);
});


//미리보기 데이터 api 연결
//키워드 이름을 보내면 될듯??
//키워드 버튼 눌렀을 때 보내도록

// $.ajax({
//     url: '/report/load_preview/?' + $.param({
//         start: 0,
//         length: 10,
//         searchKeyword: "강다니엘"
//     }),
//     type: 'GET',
//     success: res => {
//         console.log(res);
//     },
//     error: e => {
//         console.log(e.responseText);
//         if(e.responseText["data"] != null)
//             alert(e.responseText["data"]);
//         else
//             alert(e.responseText);
//     },
// });