$(document).ready(function () {
    var wc_length = $('.wc-tab').length;
    for (var i = 0; i < wc_length; i++) {
        tag = $('.wc-tab').eq(i)
        json_string = tag.attr('wc-data').trim();
        json_string = json_string.replaceAll('(', '[');
        json_string = json_string.replaceAll(')', ']');
        json_string = json_string.replaceAll('{', '[');
        json_string = json_string.replaceAll('}', ']');
        json_string = json_string.replaceAll('\'', '\"');
        wc_list = JSON.parse(json_string);
        wc_dataset = new Array();
        for (j in wc_list) {
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
                    .attr("transform", "translate(320,200)")
                    .selectAll("text")
                    .data(words)
                    .enter().append("text")
                    .style("font-size", function (d) {
                        return (Math.log2(d.mount) + 1.0) * 6 + "px";
                    })
                    .attr("transform", function (d) {
                        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                    })
                    .text(function (d) {
                        return d.subject;
                    });
            })
            .spiral('archimedean')
            .start();
    }
});