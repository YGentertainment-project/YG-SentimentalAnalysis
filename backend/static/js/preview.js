$(document).ready(function () {
    var wc_length = $('.wc-tab').length;
    for (var i = 0; i < wc_length; i++) {
        tag = $('.wc-tab').eq(i)
        // Python List[Tuple[str, int]] -> Json 변환
        json_string = tag.attr('wc-data').trim();
        json_string = json_string.replaceAll('(', '[');
        json_string = json_string.replaceAll(')', ']');
        json_string = json_string.replaceAll('{', '[');
        json_string = json_string.replaceAll('}', ']');
        json_string = json_string.replaceAll('\'', '\"');
        wc_list = JSON.parse(json_string);
        wc_dataset = new Array();
        tag_id = "#" + tag.attr('id');
        console.log(tag_id);
        // 워드 클라우드 생성용 데이터셋 제작
        // subject: 텍스트, amount: 양
        for (j in wc_list) {
            if (wc_dataset.length >= 40) {
                break;
            }
            if (wc_list[j][1] > 1 && wc_list[j][0].length > 1) {
                console.log(wc_list[j]);
                new_dict = {};
                new_dict['subject'] = wc_list[j][0];
                new_dict['amount'] = wc_list[j][1];
                wc_dataset.push(new_dict);
            }
        }
        console.log('Dataset', wc_dataset);
        height = tag.height();
        width = tag.width();
        d3.layout.cloud().size([700, 350])
            .words(wc_dataset)
            .rotate(0)
            .fontSize(function (d) {
                // 수량에 따른 글씨 크기 조정 함수
                // 현재 값에 (log2(value) + 1) * 6을 사용
                return (Math.log2(d.amount) + 1) * 6;
            })
            .padding(5)
            .on("end", function (words) {
                d3.select(tag_id).append("svg")
                    .attr("width", 700)
                    .attr("height", 350)
                    .attr("class", "wordcloud")
                    .append("g")
                    .attr("transform", "translate(350,175)")
                    .selectAll("text")
                    .data(words)
                    .enter().append("text")
                    .style("font-size", function (d) {
                        return d.size + "px";
                    })
                    .style('fill', 'black')
                    .attr("transform", function (d) {
                        // 위치 변환
                        return "translate(" + [d.x, d.y] + ")";
                    })
                    .attr("text-anchor", "middle")
                    .text(function (d) {
                        // 워드클라우드 텍스트
                        return d.subject;
                    });
            })
            // 워드클라우드 형태 함수
            .spiral('archimedean') 
            .start();
    }
});