//그룹 신규 등록 popup 관련
 $("#add-group").click(function(){
     // +버튼
    document.getElementById("add-group-form").style.display = "flex";
 });

 $("#add-group-form-close").click(function(){
     // 닫기
    document.getElementById("add-group-form").style.display = "none";
 });

 $("#add-group-form-save").click(function(){
     // 저장 후 팝업 닫기
    let newButton = document.createElement('input');
    newButton.innerHTML = `
        <input type="button" class="group-btn" value="{{${$("#new_group_name").val()}}}">
    `;
    $('#groups').append(newButton);
    document.getElementById("add-group-form").style.display = "none";
 });

 $(".group-btn").click(function(){
    console.log($(this).val());
    if($(this).hasClass("clicked-group-btn")){
        $(this).removeClass("clicked-group-btn");
    }else{
        $(this).addClass("clicked-group-btn");
        $(".group-btn").not($(this)).removeClass("clicked-group-btn");  
    }
    //TODO: 맞는 정보로 가져오기

 });

//키워드 버튼 누르면 변하도록
 $(".keyword-btn").click(function(){
    if($(this).hasClass("clicked-border-btn")){
        $(this).removeClass("clicked-border-btn");
    } else {
        $(this).addClass("clicked-border-btn");
    }
 });

 //뉴스 수집 기간 누르면 변하도록
 $(".collect-date-btn").click(function(){
    if($(this).hasClass("clicked-border-btn")){
        $(this).removeClass("clicked-border-btn");
    }else{
        $(this).addClass("clicked-border-btn");
        $(".collect-date-btn").not($(this)).removeClass("clicked-border-btn");  
    }
    console.log("click");
 });

  //그룹 저장
  $("#save-group").click(function(){
    console.log("그룹 저장");

    var group_name = $('.clicked-group-btn').val();
    console.log(group_name);

    var keywords = $(".keyword-btn").find('.clicked-border-btn').val();
    console.log(keywords);
    
    var collect_date = $(".collect-date-btn").find('.clicked-border-btn').val();
    console.log(collect_date);
 });
