// return data for child rows(snippet, reaction)
function format(d){
    var snippet = "<a href="+'"'+d.url+'"'+"target="+'"'+"_blank"+'"'+">"+d.snippet+'...'+"</a>";
    var reaction_ko = {
        'cheer': '응원해요',
        'congrats': '축하해요',
        'expect': '기대해요',
        'like': '좋아요',
        'sad': '슬퍼요',
        'surprise': '놀랐어요'
    }
    var reaction = '';
    for (var react in d.reaction) {
        reaction += '<br>' + reaction_ko[react] + ': ' + d.reaction[react]
    }
    
    console.log(reaction);
    reaction += '<br>'
    return snippet+reaction;
}

$(document).ready(function(){
    // create datatables
    var dt = $('#dataTable').DataTable({
        serverSide: true,
        ajax: {
            url: '/report/load_data',
            type: 'GET',
            data: 'data',
        },
        columns: [
            {data: 'title'},
            {data: 'keyword'},
            {data: 'create_dt'},
            {data: 'press'},
        ],
        // disable ordering with column 0(title), 1(keyword), 3(press)
        columnDefs: [
            { orderable: false, targets: 0 },
            { orderable: false, targets: 1 },
            { orderable: false, targets: 3 },
         ],
        // set default ordering column to 2(create_dt) descending
        order: [[2, 'desc']],
        // for return key to search
        search: { return: true}
    })

    // child rows
    // Array to track the ids of the details displayed rows
    var detailRows = [];

    $('#dataTable tbody').on('click', 'tr', function () {
        var tr = $(this).closest('tr');
        var row = dt.row( tr );
        var idx = $.inArray( tr.attr('id'), detailRows );

        if ( row.child.isShown() ) {
            tr.removeClass( 'details' );
            row.child.hide();

            // Remove from the 'open' array
            detailRows.splice( idx, 1 );
        }
        else {
            tr.addClass( 'details' );
            row.child( format( row.data() ) ).show();

            // Add to the 'open' array
            if ( idx === -1 ) {
                detailRows.push( tr.attr('id') );
            }
        }
    } );

    // On each draw, loop over the `detailRows` array and show any child rows
    dt.on( 'draw', function () {
        $.each( detailRows, function ( i, id ) {
            $('#'+id+' td.details-control').trigger( 'click' );
        } );
    } );

    // for hide searching form and setting number of rows in datatable
    $('#dataTable_filter').remove();

    $("#searchBtn").click(function () {

        // initialize search value per columns
        var numCols = dt.columns().nodes().length;
        for(var i=0; i<numCols; i++) { dt.column(i).search(''); }

        var searchPress = $("#searchPress").val();
        var searchDate = $("#searchDateFrom").val() + "~" + $("#searchDateTo").val()
        var searchTitle = $("#searchTitle").val();
        var searchKeyword = $("#searchKeyword").val();

        // datatables search API
        dt.columns(0).search(searchTitle);
        dt.columns(1).search(searchKeyword);
        if($("#searchDateFrom").val()!=""&&$("#searchDateTo").val()!="") dt.columns(2).search(searchDate);
        dt.columns(3).search(searchPress).draw();

    });
})