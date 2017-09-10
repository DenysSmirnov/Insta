var comments = 2; // - количество отображаемых комментов
    hidecom = "Скрыть комментарии";
    showcom = "Показать все комментарии";

    $(".archive").html( showcom );
    $("._hdiv:not(:lt("+comments+"))").hide();

    $(".archive").click(function (e){
      e.preventDefault();
      if( $("._hdiv:eq("+comments+")").is(":hidden") )
      {
        $("._hdiv:hidden").show();
        $(".archive").html( hidecom );
      }
      else
      {
        $("._hdiv:not(:lt("+comments+"))").hide();
        $(".archive").html( showcom );
      }
    });