$('._q8y0e').click(function(){
  document.querySelector('.sets').style.display='block';
    });

$(document).mouseup(function (e){
        var div = $('._784q7');
        if (!div.is(e.target)
            && div.has(e.target).length === 0) {
            document.querySelector('.sets').style.display='none';
        }
    });

document.querySelectorAll('._h74gn')[2].addEventListener
        ('mouseup', function() {
          document.querySelector('.sets').style.display='none';  
        });