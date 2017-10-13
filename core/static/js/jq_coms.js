var list = $('._listcoms');

list.each(function () {
  var item = $(this).find('._hdiv'),
      item_target = item.filter(function () {
        return $(this).index() > 2
      });
  var showcom = "Показать еще комментарии ("+item_target.length+")";
  var link = $('<a class="archive">'+showcom+'</a>').click(function(e) {
    e.preventDefault();
    item_target.toggle(this);
    if( $(e.target).text() === showcom )
    {
      $(this).text("Скрыть комментарии");
    } else {
      $(this).text(showcom);
    }
  });

  item_target.hide().eq(0).before(link);
});