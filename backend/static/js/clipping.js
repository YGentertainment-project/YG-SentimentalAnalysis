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
    var len =  document.getElementById('schedule-body').childElementCount;
    const tableRow = $('<tr></tr>');
    // #차
    let dataCol = document.createElement('td');
    dataCol.innerHTML = `
    <td>
        <div class="row_layout" style="font-weight: bold; font-size: 12px;">
            ${len+1}차
        </div>
    </td>
    `;
    tableRow.append(dataCol);


    let dataCol2 = document.createElement('td');
    dataCol2.innerHTML = `
    <td>
        <div class="row_layout">
            <div style="width:80px;">
                <select name="hour" id="hour-select" class="form-select schedule-hour">
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
                <select name="minute" id="minute-select" class="form-select schedule-minute">
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
 });



  //그룹 저장(api 연결)
  $("#save-group").click(function(){
    console.log("그룹 저장");

    //그룹 이름
    var group_name = $('.clicked-group-btn').val();
    console.log(group_name);

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
    console.log(keywords_list);

    //당일 or 어제
    var collect_date = $('.clicked-collect-date-btn').val();
    console.log(collect_date);

    //스케줄 관련
    var schedules_list = [];
    var hours = $('.schedule-hour');

	len = hours.length;
	if(len > 0) {
		for(var i = 0; i < len; i++) {
            console.log($($('.schedule-hour')[i]).val());
            schedules_list.push($($('.schedule-hour')[i]).val());
		}
	}

    console.log(schedules_list);

    var data = {
        "name": group_name,
	    "keywords": keywords_list,
	    "collect_date": collect_date,//당일/어제/1주/1달??
	    // "users": file,//file형태로 전달
	    "schedules":schedules_list
    }
    $.ajax({
        url: '/clipping/api/clipgroup',
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
    if (confirm("삭제하시겠습니까?")) {
        console.log("그룹 삭제");
        //그룹 이름
        var group_name = $('.clicked-group-btn').val();
        console.log(group_name);
        var data = {
            "name": group_name
        }
        $.ajax({
            url: 'clipping/api/clipgroup',
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


