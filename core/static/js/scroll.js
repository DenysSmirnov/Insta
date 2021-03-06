$(document).ready(function($) {
let host = window.location.hostname,
    path = 'https://s3.us-east-2.amazonaws.com/insta-s3-bucket/upload/';
if (host === '127.0.0.1') {
    path = '/static/upload/resized-images/';
}

function fix_size(){
    let images = $('.img-container img');
    images.each(setsize);
    
    function setsize(){
        let img = $(this),
            img_dom = img.get(0),
            container = img.parents('.img-container');
        if (img_dom.complete) {
            resize();
        } else img.one('load', resize);

        function resize(){
            container.height(container.width());
            if ((container.width() / container.height()) > (img_dom.width / img_dom.height)){
                img.width('100%');
                img.height('auto');
            } else {
                img.height('100%');
                img.width('auto');
            }
            let marginx=(img.width()-container.width())/-2,
                marginy=(img.height()-container.height())/-2;
            img.css({'margin-left': marginx, 'margin-top': marginy});  
        }
    }
}

$(window).on('resize', fix_size);
fix_size();

let inProgress = false,
    startFrom = $("#ph123:last a:eq(-1)")[0].search.split('=')[1];
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 100 && !inProgress){
        $.ajax({
            url: window.location.href,
            method: 'POST',
            data: {"startFrom" : startFrom},
            beforeSend: function(){
                inProgress = true;
                $("#loader2").css("display", "block").animate({"opacity": 1}, 500);
            }
        }).done(function(data){
            data = JSON.parse(data);
            $("#loader2").animate({"opacity": 0}, 500, function(){
                $("#loader2").css("display", "");
            });
            if (data.length > 0) {
                $.each(data, function(index, img) {
                photos = `<div class='img-container' style='margin-right: 4px;'>
                <a href='/detail/?_id=${img._id.$oid}'><img src='${path}${img.path}'></a></div>`;
                $("#ph123").append(photos);
                inProgress = false;
                startFrom = img._id.$oid;
                })
            }})
        }
        fix_size();
    })
});