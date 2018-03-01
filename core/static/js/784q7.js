$('._q8y0e').on('click', function() {
  $('.sets').css('display','block');
})

$(document).on('mouseup', function(e) {
    var div = $('._784q7');
    if (!div.is(e.target) && div.has(e.target).length === 0) {
        $('.sets').css('display','none');
    }
})

$('._h74gn:eq(2)').on('mouseup', function() {
    $('.sets').css('display','none');  
})