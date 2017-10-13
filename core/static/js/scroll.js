$(document).ready(function(){
    function fix_size() {
        var images = $('.img-container img');
        images.each(setsize);

        function setsize() {
            var img = $(this),
                img_dom = img.get(0),
                container = img.parents('.img-container');
            if (img_dom.complete) {
                resize();
            } else img.one('load', resize);

            function resize() {
                container.height(container.width());
                if ((container.width() / container.height()) > (img_dom.width / img_dom.height)) {
                    img.width('100%');
                    img.height('auto');
                } else {
                    img.height('100%');
                    img.width('auto');
                }
                var marginx=(img.width()-container.width())/-2,
                    marginy=(img.height()-container.height())/-2;
               // console.log(marginx);
               img.css({'margin-left': marginx, 'margin-top': marginy});  
            }
        }
    }
    $(window).on('resize', fix_size);
    fix_size();

/* Переменная-флаг для отслеживания того, происходит ли в данный момент ajax-запрос. В самом начале даем ей значение false, т.е. запрос не в процессе выполнения */
var inProgress = false;
/* С какой статьи надо делать выборку из базы при ajax-запросе */
// var startFrom = 6;
var startFrom = $("#ph123:last a:eq(-1)")[0].search.split('=')[1];

    /* Используйте вариант $('#more').click(function() для того, чтобы дать пользователю возможность управлять процессом, кликая по кнопке "Дальше" под блоком статей */
    $(window).scroll(function() {

        /* Если высота окна + высота прокрутки больше или равны высоте всего документа и ajax-запрос в настоящий момент не выполняется, то запускаем ajax-запрос */
        if($(window).scrollTop() + $(window).height() >= $(document).height() - 200 && !inProgress) {
        
        $.ajax({
            /* адрес файла-обработчика запроса */
            url: window.location.href,
            /* метод отправки данных */
            method: 'POST',
            /* данные, которые мы передаем в файл-обработчик */
            data: {"startFrom" : startFrom},
            /* что нужно сделать до отправки запроса */
            beforeSend: function() {
            /* меняем значение флага на true, т.е. запрос сейчас в процессе выполнения */
            inProgress = true;}
            /* что нужно сделать по факту выполнения запроса */
            }).done(function(data){
            // console.log(startFrom)
            /* Преобразуем результат, пришедший от обработчика - преобразуем json-строку обратно в массив */
            img = JSON.parse(data);
            // console.log(data)
            /* Если массив не пуст (т.е. статьи там есть) */
            if (img.length > 0) {
                /* Делаем проход по каждому результату, оказвашемуся в массиве,
                где в index попадает индекс текущего элемента массива, а в data - сама статья */
                $.each(img, function(index, img){
                /* Отбираем по идентификатору блок со статьями и дозаполняем его новыми данными */
                photos = "<div class='img-container' style='margin-right: 4px;'><a href='/detail/?_id="+img._id.$oid+
                "'><img src='https://s3.us-east-2.amazonaws.com/insta-s3-bucket/upload/"+img.path+"'></a></div>";
                $("#ph123").append(photos);
                /* По факту окончания запроса снова меняем значение флага на false */
                inProgress = false;
                // Увеличиваем на 10 порядковый номер статьи, с которой надо начинать выборку из базы
                startFrom = img._id.$oid;
                });
            }});
        }
        $(window).on('resize', fix_size);
            fix_size();
    });
});