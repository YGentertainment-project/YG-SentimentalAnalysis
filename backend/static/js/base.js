// csrf 토큰을 가져옵니다.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$(function(){
    var duration = 300;

    var $side = $('.sidebar');
    var $header = $('.header');
    var $dataform = $('.forms');
    $side.addClass('open');
    var $sidebt = $('.sidebar-btn').on('click', function(){
        $side.toggleClass('open');

        if($side.hasClass('open')) {
            $side.stop(true).animate({left:'0px'}, duration);
            $header.stop(true).animate({left:'250px',width:'85%'}, duration);
            $dataform.stop(true).animate({left:'250px',width:'80%'}, duration);
            $sidebt.stop(true).animate({left:'220px'}, duration);
            $sidebt.find('span').html('<i class="fas fa-chevron-left"></i>');
        }else{
            $side.stop(true).animate({left:'-220px'}, duration);
            $header.stop(true).animate({left:'50px',width:'90%'}, duration);
            $dataform.stop(true).animate({left:'50px',width:'90%'}, duration);
            $sidebt.stop(true).animate({left:'0px'}, duration);
            $sidebt.find('span').html('<i class="fas fa-chevron-right"></i>');
        };
    });
});