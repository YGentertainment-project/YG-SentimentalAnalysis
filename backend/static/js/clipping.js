function getTime(minutes, seconds) {
    minutes = parseInt(minutes);
    seconds = parseInt(seconds);
    //Optional: Add leading zero's
    if (minutes < 10)
        minutes = '0'+minutes;
 
    if (seconds < 10)
        seconds = '0'+seconds;
 
    //Return the current minutes and seconds
    return minutes+':'+seconds;
 }


//그룹 신규 등록 popup 관련
 $("#add-group").click(function(){
     // +버튼
    $("#new_group_name").val("");
    document.getElementById("add-group-form").style.display = "flex";
 });

 $("#add-group-form-close").click(function(){
     // 닫기
    document.getElementById("add-group-form").style.display = "none";
 });

 $("#add-group-form-save").click(function(){
    // 저장 후 팝업 닫기
    let newButton = $('<input class="group-btn" type="button" value="'+$("#new_group_name").val()+'"></input>');
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
    if($(widget).hasClass("clicked-group-btn")){
        $(widget).removeClass("clicked-group-btn");
        $("#group_content").addClass("hide");
    }else{
        $(widget).addClass("clicked-group-btn");
        $(".group-btn").not($(widget)).removeClass("clicked-group-btn"); 
        $("#group_content").removeClass("hide");
        //content 보여줄 때 해당 그룹이름과 맞게 가져오기
        console.log($(widget).val());
        getKeywordOfGroup($(widget).val());
    }
 }

function getKeywordOfGroup(group_name){
    //TODO: get api 연결
    //일단 dummy data로 연결하기
    $.ajax({
        url: '/clipping/clipgroup/?' + $.param({
            group: group_name
        }),
        type: 'GET',
        datatype: 'json',
        contentType: 'application/json; charset=utf-8',
        success: res => {
            console.log("success");
            console.log(res);
            var keywords = ["키워드1", "키워드3", "키워드8"];
            var collectdate = true;
            var schedules = ["1:1", "1:2", "1:3"];

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
            if(collectdate){
                collectdate = "당일";
            }else{
                collectdate = "어제";
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
}

//키워드 버튼 누르면 변하도록
 $(".keyword-btn").click(function(){
    if($(this).hasClass("clicked-keyword-btn")){
        $(this).removeClass("clicked-keyword-btn");
    } else {
        $(this).addClass("clicked-keyword-btn");
    }
 });

 //뉴스 수집 기간 누르면 변하도록
 $(".collect-date-btn").click(function(){
    if($(this).hasClass("clicked-collect-date-btn")){
        $(this).removeClass("clicked-collect-date-btn");
    }else{
        $(this).addClass("clicked-collect-date-btn");
        $(".collect-date-btn").not($(this)).removeClass("clicked-collect-date-btn");  
    }
    console.log("click");
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
    console.log("그룹 저장");
    //그룹 이름
    var group_name = $('.clicked-group-btn').val();
    //키워드들
    var keywords = $('.clicked-keyword-btn');
	var len = keywords.length;
    var keywords_list = [];
	if(len > 0) {
		for(var i = 0; i < len; i++) {
            console.log($($('.clicked-keyword-btn')[i]).val());
            keywords_list.push($($('.clicked-keyword-btn')[i]).val());
		}	
	}
    //당일 or 어제
    var collect_date = $('.clicked-collect-date-btn').val();
    if(collect_date=="당일"){
        collect_date = true;
    }else if(collect_date=="어제"){
        collect_date = false;
    }
    //스케줄 관련
    var schedules_list = [];
    var hours = $('.schedule-hour');
	len = hours.length;
	if(len > 0) {
		for(var i = 0; i < len; i++) {
            //$($('.schedule-hour')[i]).val()
            //$($('.schedule-minute')[i]).val()
            schedules_list.push(getTime($($('.schedule-hour')[i]).val(), $($('.schedule-minute')[i]).val()));
		}
	}
    if(collect_date==undefined && keywords_list.length == 0){
        alert("모든 값을 입력해주세요.");
        return;
    }
    var data = {
        "name": group_name,
	    "keywords": keywords_list,
	    "collect_date": collect_date,//boolean
	    // "users": file,//file형태로 전달
	    "schedules":schedules_list
    }
    console.log(data);
    $.ajax({
        url: '/clipping/clipgroup/',
        type: 'POST',
        datatype:'json',
        data: JSON.stringify(data),
        success: res => {
            alert("저장되었습니다.");
        },
        error: e => {
            console.log(e.responseText);
            alert(e.responseText);
        },
    })
 });


  //그룹 삭제(api 연결)
  $("#delete-group").click(function(){
    var group_name = $('.clicked-group-btn').val();
    if(group_name == undefined){
        alert("삭제할 그룹을 선택해주세요.");
    }
    else if (confirm("삭제하시겠습니까?")) {
        var data = {
            "name": group_name
        }
        $.ajax({
            url: 'clipping/clipgroup/',
            type: 'delete',
            datatype:'json',
            data: JSON.stringify(data),
            success: res => {
                alert("삭제되었습니다.");
            },
            error: e => {
                console.log(e.responseText);
                alert(e.responseText);
            },
        })
    } 
 });


