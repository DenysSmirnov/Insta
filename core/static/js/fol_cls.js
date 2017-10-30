$(document).mouseup(function(e){
var div = $('._784q7');
if (!div.is(e.target) && div.has(e.target).length === 0) {
    history.back(-1);
} else {
    div2 = $('input._t78yp, ._gexxb');
    if ( div2.is(e.target) ) {
        var user = e.target.id;
        $.post('/ajax_/', {"ufol" : user}).done(function(data) {
        if (data === '1') {
            e.target.value = 'Подписки';
            $('#'+user).removeClass('_gexxb').addClass('_t78yp');
        } else {
            e.target.value = 'Подписаться';
            $('#'+user).removeClass('_t78yp').addClass('_gexxb');
        }
        })
    }
}
})