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
        // 워드 클라우드 생성용 데이터셋 제작
        // subject: 텍스트, mount: 양
        for (j in wc_list) {
            if (wc_dataset.length >= 20) {
                break;
            }
            if (wc_list[j][1] > 2) {
                new_dict = {};
                new_dict['subject'] = wc_list[j][0];
                new_dict['mount'] = wc_list[j][1];
                wc_dataset.push(new_dict);
            }
        }
        temp = wc_dataset;
        height = tag.height();
        width = tag.width();
        tag_id = "#" + tag.attr('id');
        console.log(tag_id)
        d3.layout.cloud().size([700, 300])
            .words(wc_dataset)
            .rotate(0)
            .fontSize(function (d) {
                return d.mount;
            })
            .on("end", function (words) {
                d3.select(tag_id).append("svg")
                    .attr("width", 700)
                    .attr("height", 300)
                    .attr("class", "wordcloud")
                    .append("g")
                    .attr("transform", "translate(350,150)")
                    .selectAll("text")
                    .data(words)
                    .enter().append("text")
                    .style("font-size", function (d) {
                        // 수량에 따른 글씨 크기 조정 함수
                        // 현재 값에 (log2(value) + 1) * 6을 사용
                        return (Math.log2(d.mount) + 1.0) * 8 + "px";
                        // return 20 + "px";
                    })
                    .style('fill', 'black')
                    .attr("transform", function (d) {
                        // 위치 변환
                        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                    })
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