const api_domain = "/crawler/api/"

$(document).ready(function(){
    let crawlTarget = 'News';

    $.ajax({
        url: api_domain + 'schedule/',
        type: 'GET',
        datatype:'json',
        contentType: 'application/json; charset=utf-8',
        success: res => {
           const {
               hour, minute
           } = res;
           $("#scheduleHour").val(hour);
           $("#scheduleMinute").val(minute);
        },
        error: e => {
            alert('Error occured');
        },
    })

    $('#change-schedule').click(() => {
        const hour = $("#scheduleHour").val();
        const minute = $("#scheduleMinute").val();
        $.ajax({
            url: api_domain + 'schedule/',
            type: 'PUT',
            data: JSON.stringify({hour, minute}),
            datatype: 'json',
            contentType: 'application/json; charset=utf-8',
            success: res => {
                alert('Schedule has been changed')
            },
            error: e => {
                console.log('error')
            },
        })
    })


    $('#crawl-select').change((e) => {
        crawlTarget = e.target.value
    })
    $('#start-crawl').click(() => {
        console.log(crawlTarget);
        const from_date = $("#fromDate").val()
        const to_date = $("#toDate").val()

        $.ajax({
            url: api_domain + 'crawl/',
            type: 'POST',
            data: JSON.stringify({"name": crawlTarget, from_date, to_date}),
            datatype:'json',
            contentType: 'application/json; charset=utf-8',
            success: res => {
               console.log(res);
            },
            error: e => {
                alert('Failed to send request for scraping')
            },
        })
    })
})