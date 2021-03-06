$(function($) {
let host = window.location.hostname,
    input = $('._avvq0'),
    path = 'https://s3.us-east-2.amazonaws.com/insta-s3-bucket/upload/';
if (host === '127.0.0.1') {
    path = '/static/upload/resized-images/';
}

//Живой поиск "change keyup input click"
input.on("input", function() {
  if (this.value.trim()) {  // .length >= 2
    $.ajax({
      url: '/search/',
      type: 'POST', 
      data: {'referal': this.value},
      beforeSend: function(){
        $("#loader_small").css("display", "block");
      }
    }).done(function(data) {
      $("#loader_small").css("display", "");
      $("._h0otu").remove();
      $("._5ayw3, ._ohiyl").append("<div class='_h0otu'><div class='_9xy3k'></div><div class='_dv59m'><div class='_etpgz'></div></div></div>");
      if (!data) {
        $("._etpgz").empty().html("<div class='_oznku'>Ничего не найдено</div>");
      } else {
        data = JSON.parse(data);
        // console.log(data)
        $.each(data, function(i, item) {
          if (i === 0) {
            $.each(item, function(index, img) {
              let li = `<a class='_gimca' href='/${img.name}/'><div class='_t3f9x'>
                <img class='_a4egj' src='${path}${img.avatar}'><div class='_cuwjc'><div class='_ajwor'>
                <span class='_sgi9z'>${img.name}</span></div>${isFio(img.fio)}</div></div></a>`;
              $("._etpgz").append(li);
            })
          }
          if (i === 1) {
            let a = [];
            $.each (item, function(index, img) {
              $.each (img.tags, function(index, tag) {
                if (tag.indexOf(input.val().toLowerCase()) + 1) {
                  a.push(tag);
                }
              })
            });
            a.sort();
            i = a.length;
            let b = 1;
            while (i--) {
              if (a[i] === a[i-1]) {
                a.splice(i, 1);
                b += 1;
              } else {
                let li = `<a class='_gimca' href='/explore/?tag=${encodeURIComponent(a[i])}'><div class='_t3f9x'>
                    <img class='_a4tag' src='/static/ico/_resheto.png'><div class='_cuwjc'><div class='_ajwor'>
                    <span class='_sgi9z'>${a[i]}</span></div><span class='_sayjy'>${b} публикаций</span></div></div></a>`;
                $("._etpgz").append(li);
                b = 1;
              }
            }
          }
        })
      }
    })
  } else {
    $("._h0otu").remove();
  }
});

input.on("click", () => $('._h0otu').show());

$(document).on("click", e => {
  let div = $('._h0otu');
  if (!div.is(e.target) && div.has(e.target).length === 0 && !input.is(e.target)){
    div.fadeOut();
  }
});

function isFio(fio) {
  if (fio){
    return `<span class='_sayjy'>${fio}</span>`
  }
  return ''
}

});