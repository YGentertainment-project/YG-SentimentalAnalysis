// 00:00:00형태로 반환
function getTime(minutes, seconds) {
    minutes = parseInt(minutes);
    seconds = parseInt(seconds);
    if (minutes < 10)
        minutes = '0'+minutes;
    if (seconds < 10)
        seconds = '0'+seconds;
    return minutes+':'+seconds+':00';
 }


//그룹 신규 등록 popup 관련
 $("#add-group").click(function(){
     // +버튼
    $("#new_group_name").val("");
    document.getElementById("add-group-form").style.display = "flex";
 });

 $("#add-group-form-close").click(function(){
     // popup 닫기
    document.getElementById("add-group-form").style.display = "none";
 });

 $("#add-group-form-save").click(function(){
    // 저장 후 팝업 닫기
    // 새로 생겼다는 의미로 id '-1' 넣어두기
    let newButton = $('<input class="group-btn" type="button" value="'+$("#new_group_name").val()+'" id="'+-1+'"></input>');
    newButton.click(function(){
        click_group_function(newButton);
    });
    $('#groups').append(newButton);
    document.getElementById("add-group-form").style.display = "none";
    if($(newButton).hasClass("clicked-group-btn")){
        $(newButton).removeClass("clicked-group-btn");
        $("#group_content").addClass("hide");
    }else{
        $(newButton).addClass("clicked-group-btn");
        $(".group-btn").not($(newButton)).removeClass("clicked-group-btn"); 
        $("#group_content").removeClass("hide");
        getNewKeywordOfGroup();
    }
 });

 $(".group-btn").click(function(){
    click_group_function(this);
 });

 function click_group_function(widget){
     //지금 눌려있는 애가 저장되지 않은 새로 만든 그룹이라면
    if($('.clicked-group-btn').attr('id') == -1){
        alert("먼저 새로운 그룹 저장을 해주세요.");
        return;
    }
    else if($(widget).hasClass("clicked-group-btn")){
        $(widget).removeClass("clicked-group-btn");
        $("#group_content").addClass("hide");
    }else{
        $(widget).addClass("clicked-group-btn");
        $(".group-btn").not($(widget)).removeClass("clicked-group-btn"); 
        $("#group_content").removeClass("hide");
        //content 보여줄 때 해당 그룹이름과 맞게 가져오기
        getKeywordOfGroup($(widget).attr('id'));
        $('#receiver_download_group_id').val($(widget).attr('id'));
    }
    $("#receiver-upload").val("");
 }

function getKeywordOfGroup(group_id){
    $.ajax({
        url: '/clipping/clipgroup/?' + $.param({
            group_id: group_id
        }),
        type: 'GET',
        datatype: 'json',
        contentType: 'application/json; charset=utf-8',
        success: res => {
            var keywords = res.data["checked_keywords"];
            var collectdate = res.data["collect_date"];
            var schedules = res.data["schedule"];

            //키워드들
            var len = $(".keyword-btn").length;
            if(len > 0) {
                for(var i = 0; i < len; i++) {
                    if( keywords.includes($($('.keyword-btn')[i]).val()) ){
                        $($('.keyword-btn')[i]).addClass("clicked-keyword-btn");
                    }else{
                        $($('.keyword-btn')[i]).removeClass("clicked-keyword-btn");
                    }
                }	
            }
            //뉴스 수집 기간
            if(collectdate == 1){
                collectdate = "당일";
            }else if(collectdate == 0){
                collectdate = "어제";
            }else if(collectdate == 2){
                collectdate = "1주";
            }else if(collectdate == 3){
                collectdate = "1달";
            }
            len = $(".collect-date-btn").length;
            if(len > 0) {
                for(var i = 0; i < len; i++) {
                    if(collectdate == $($('.collect-date-btn')[i]).val()){
                        $($('.collect-date-btn')[i]).addClass("clicked-collect-date-btn");
                    }else{
                        $($('.collect-date-btn')[i]).removeClass("clicked-collect-date-btn");
                    }
                }	
            }
            //메일 발송 설정
            $('#schedule-body').empty();
            for(var i=0; i<schedules.length;i++){
                add_schedule_function(schedules[i]);
            }
        },
        error: e => {
            if(e.responseText["data"] != null)
                alert(e.responseText["data"]);
            else
                alert(e.responseText);
        },
    });
}

function getNewKeywordOfGroup(){
    //신규 버튼 누르고 빈 contents 보여줄 때
    //키워드들
    var len = $(".keyword-btn").length;
    if(len > 0) {
        for(var i = 0; i < len; i++) {
            $($('.keyword-btn')[i]).removeClass("clicked-keyword-btn");
        }	
    }
    //뉴스 수집 기간
    len = $(".collect-date-btn").length;
    if(len > 0) {
        for(var i = 0; i < len; i++) {
            $($('.collect-date-btn')[i]).removeClass("clicked-collect-date-btn");
        }	
    }
    //메일 발송 설정
    $('#schedule-body').empty();
    for(var i=0; i<1; i++){
        add_schedule_function();
    }
    $('#receiver_download_group_id').val("");
}

//키워드 버튼 누르면 클릭된 상태가 되도록
 $(".keyword-btn").click(function(){
    if($(this).hasClass("clicked-keyword-btn")){
        $(this).removeClass("clicked-keyword-btn");
    } else {
        $(this).addClass("clicked-keyword-btn");
    }
 });

 //뉴스 수집 기간 누르면 클릭된 상태가 되도록
 $(".collect-date-btn").click(function(){
    if($(this).hasClass("clicked-collect-date-btn")){
        $(this).removeClass("clicked-collect-date-btn");
    }else{
        $(this).addClass("clicked-collect-date-btn");
        $(".collect-date-btn").not($(this)).removeClass("clicked-collect-date-btn");  
    }
 });

 //스케줄 + 버튼 누르면
 $("#add-schedule").click(function(){
    add_schedule_function();
 });


 function add_schedule_function(time){
    var len =  document.getElementById('schedule-body').childElementCount;
    const tableRow = $('<tr></tr>');
    // #차
    let dataCol = document.createElement('td');
    if(len==0){//+버튼 있어야함
        dataCol.innerHTML = `
        <td>
            <div class="row_layout" style="font-weight: bold; font-size: 12px;">
                1차
                <svg id="add-schedule" width="15" height="15" viewBox="0 0 100 100" class="add-circle"
                    style="margin-left: 3px; margin-top: 2px;" onclick="add_schedule_function()">
                    <g stroke = "black" stroke-width = "12" fill="none">
                        <path d="M 25 50 L 75 50
                            M 50 25 L 50 75
                            M 50 5
                            A 45 45 0 0 0 50 95
                            A 45 45 0 1 0 5 50" />
                    </g>
                </svg>
            </div>
        </td>
        `;
    }else{
        dataCol.innerHTML = `
        <td>
            <div class="row_layout" style="font-weight: bold; font-size: 12px;">
                ${len+1}차
            </div>
        </td>
        `;
    }
    tableRow.append(dataCol);

    let dataCol2 = document.createElement('td');
    dataCol2.innerHTML = `
    <td>
        <div class="row_layout">
            <div style="width:80px;">
                <select name="hour" id="hour-select${len+1}" class="form-select schedule-hour">
                    <option value="0">00</option>
                    <option value="1">01</option>
                    <option value="2">02</option>
                    <option value="3">03</option>
                    <option value="4">04</option>
                    <option value="5">05</option>
                    <option value="6">06</option>
                    <option value="7">07</option>
                    <option value="8">08</option>
                    <option value="9">09</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                    <option value="13">13</option>
                    <option value="14">14</option>
                    <option value="15">15</option>
                    <option value="16">16</option>
                    <option value="17">17</option>
                    <option value="18">18</option>
                    <option value="19">19</option>
                    <option value="20">20</option>
                    <option value="21">21</option>
                    <option value="22">22</option>
                    <option value="23">23</option>
                </select>
            </div>
            <span style="margin: 5px 10px 0 5px;">시</span>
            <div style="width:80px;">
                <select name="minute" id="minute-select${len+1}" class="form-select schedule-minute">
                    <option value="0">00</option>
                    <option value="1">01</option>
                    <option value="2">02</option>
                    <option value="3">03</option>
                    <option value="4">04</option>
                    <option value="5">05</option>
                    <option value="6">06</option>
                    <option value="7">07</option>
                    <option value="8">08</option>
                    <option value="9">09</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                    <option value="13">13</option>
                    <option value="14">14</option>
                    <option value="15">15</option>
                    <option value="16">16</option>
                    <option value="17">17</option>
                    <option value="18">18</option>
                    <option value="19">19</option>
                    <option value="20">20</option>
                    <option value="21">21</option>
                    <option value="22">22</option>
                    <option value="23">23</option>
                    <option value="24">24</option>
                    <option value="25">25</option>
                    <option value="26">26</option>
                    <option value="27">27</option>
                    <option value="28">28</option>
                    <option value="29">29</option>
                    <option value="30">30</option>
                    <option value="31">31</option>
                    <option value="32">32</option>
                    <option value="33">33</option>
                    <option value="34">34</option>
                    <option value="35">35</option>
                    <option value="36">36</option>
                    <option value="37">37</option>
                    <option value="38">38</option>
                    <option value="39">39</option>
                    <option value="40">40</option>
                    <option value="41">41</option>
                    <option value="42">42</option>
                    <option value="43">43</option>
                    <option value="44">44</option>
                    <option value="45">45</option>
                    <option value="46">46</option>
                    <option value="47">47</option>
                    <option value="48">48</option>
                    <option value="49">49</option>
                    <option value="50">50</option>
                    <option value="51">51</option>
                    <option value="52">52</option>
                    <option value="53">53</option>
                    <option value="54">54</option>
                    <option value="55">55</option>
                    <option value="56">56</option>
                    <option value="57">57</option>
                    <option value="58">58</option>
                    <option value="59">59</option>
                </select>
            </div>
            <span style="margin: 5px 10px 0 5px;">분</span>
        </div>
    </td>`;
    tableRow.append(dataCol2);

    $('#schedule-body').append(tableRow);
    if(time != null){
        time = time.split(':');
        $(`#hour-select${len+1}`).val(parseInt(time[0])).prop('selected',true);
        $(`#minute-select${len+1}`).val(parseInt(time[1])).prop('selected',true);
    }
 }



  //그룹 저장(api 연결)
$("#save-group").click(function(){
    //그룹 이름
    var group_name = $('.clicked-group-btn').val();
    //키워드들
    var keywords = $('.clicked-keyword-btn');
	var len = keywords.length;
    var keywords_list = [];
	if(len > 0) {
		for(var i = 0; i < len; i++) {
            keywords_list.push($($('.clicked-keyword-btn')[i]).val());
		}	
	}
    //당일 or 어제
    var collect_date = $('.clicked-collect-date-btn').val();
    if(collect_date=="당일"){
        collect_date = 1;
    }else if(collect_date=="어제"){
        collect_date = 0;
    }else if(collect_date=="1주"){
        collect_date = 2;
    }else if(collect_date=="1달"){
        collect_date = 3;
    }
    //스케줄 관련
    var schedules_list = [];
    var hours = $('.schedule-hour');
	len = hours.length;
	if(len > 0) {
		for(var i = 0; i < len; i++) {
            schedules_list.push(getTime($($('.schedule-hour')[i]).val(), $($('.schedule-minute')[i]).val()));
		}
	}
    if(collect_date==undefined || keywords_list.length == 0){
        alert("모든 값을 입력해주세요.");
        return;
    }
    var data = {
        "name": group_name,
	    "keywords": keywords_list,
	    "collect_date": collect_date,//boolean
	    "schedules":schedules_list
    }
    var len = $(".clicked-group-btn").length;

    // form-data로 보내기
    let file = document.getElementById("receiver-upload").files[0];
    let formData = new FormData(); 
    formData.append("users", file);
    // 다른 parameter들은 body로 묶어 보내기
    formData.append("body", JSON.stringify(data));
    $.ajax({
        url: '/clipping/clipgroup/',
        data: formData,
        type: 'POST',
        contentType: false,
        processData: false,
        success: res => {
            alert("저장되었습니다.");
            $('.clicked-group-btn').attr('id', res.group);
        },
        error: e => {
            if(e.responseText["data"] != null)
                alert(e.responseText["data"]);
            else
                alert(e.responseText);
        },
    });
 });


  //그룹 삭제(api 연결)
  $("#delete-group").click(function(){
    var group_id = $('.clicked-group-btn').attr('id');
    if(group_id == undefined){
        alert("삭제할 그룹을 선택해주세요.");
    }
    else if (confirm("삭제하시겠습니까?")) {
        //db저장이 아닌 프론트에만 있는 것이기 때문에 서버에 전달 안하고 삭제
        if(group_id == -1){
            alert("삭제되었습니다.");
            location.reload();
            return;
        }
        var data = {
            "group_id": group_id
        };
        $.ajax({
            url: '/clipping/clipgroup/?' + $.param({
                group_id: group_id
            }),
            type: 'delete',
            datatype:'json',
            data: JSON.stringify(data),
            success: res => {
                alert("삭제되었습니다.");
                location.reload();
            },
            error: e => {
                if(e.responseText["data"] != null)
                    alert(e.responseText["data"]);
                else
                    alert(e.responseText);
            },
        })
    } 
 });

//키워드: 엑셀 업로드 버튼 클릭
$('#keyword-uplaod-btn').click(function (){
    let file = document.getElementById("keyword-upload").files[0];
    if(file == undefined){
        alert("키워드 파일을 선택해주세요.");
        return;
    }
    let formData = new FormData(); 
    formData.append("KeywordFile", file);
    $.ajax({
        url: '/clipping/keyword-group/',
        data: formData,
        type: 'POST',
        contentType: false,
        processData: false,
        success: res => {
            alert("저장되었습니다.");
        },
        error: e => {
            if(e.responseText["data"] != null)
                alert(e.responseText["data"]);
            else
                alert(e.responseText);
        },
    });
});

document.querySelector("#receiver-download-btn").addEventListener("click", function(event) {
    //그룹이 저장되지 않은 상태에서 엑셀 다운로드 방지
    var group_id = $('.clicked-group-btn').attr('id');
    if(group_id == -1){
        alert("그룹을 먼저 저장한 후에 엑셀 다운로드를 할 수 있습니다.");
        event.preventDefault();
    }
}, false);


//미리보기 화면으로 이동
$("#go-to-preview").click(function(){
     //지금 눌려있는 애가 저장되지 않은 새로운 그룹이라면
    if($('.clicked-group-btn').attr('id') == -1){
        alert("먼저 새로운 그룹 저장을 해주세요.");
        return;
    }
    group_id = $('.clicked-group-btn').attr('id');
    location.href = "/clipping/preview?group_id="+group_id;
});