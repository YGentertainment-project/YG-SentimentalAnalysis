const api_domain = "/crawler/api/"

$(document).ready(function(){
    let crawlTarget = 'News'
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
                console.log(res)
            },
            error: e => {
                alert('Failed to send request for scraping')
            },
        })
    })
})