$(document).mouseup(function (e){
    var div = $('._784q7');
    if (!div.is(e.target)
        && div.has(e.target).length === 0) {
        history.back(-1);
    }
});