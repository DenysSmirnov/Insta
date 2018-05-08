(($) => {
    'use strict';
    let inProgress = false,
        startFrom = $("._cl_but:last")[0].value,
        from = -1;
    const html = $('html');

    let conf = $.post('/ajax_/', data => {
                conf = JSON.parse(data);
                });


    class Post {
        constructor(img) {
            this.author = img.author.name;
            this.avatar = img.author.avatar;
            this.title = img.title;
            this.id = img._id.$oid;
            this.path = img.path;
            this.likedUsers = img.liked_users;
            this.desc = img.description;
            this.tags = img.tags;
            this.comments = img.comments;
            this.createdTime = img.created_time.$date;
        }
        static runAjax(args) {
            let jqxhr = $.ajax({
                url: '/ajax_/',
                type: 'POST',
                data: args,
                statusCode: {
                    500: () => alert( "Переданы некорректные данные!" )
                },
                beforeSend: () => inProgress = true
            });
            return jqxhr;
        }
        static like(e) {
            let id = $(this).val();
            if (!inProgress) {
                Post.runAjax({"like": id})
                .done(data => {
                    let btn = $(e.target).parent(); // all browsers
                    if ($('._cl_but').is(e.target)) {
                        btn = $(e.target); // firefox
                    }
                    let count = btn.siblings('._like').find($("._likecount")),
                        c;
                    if (data === '1') {
                        $("img", btn).attr("src", "/static/ico/heart_red.png");
                        if (count.length === 1) {
                            c = parseInt(count.text()) + 1;
                        } else {
                            btn.after("<span class='_like'>Нравится: <span class='_likecount'>1</span></span>");
                            c = 1;
                        }
                    } else {
                        $("img", btn).attr("src", "/static/ico/heart_white.png");
                        c = parseInt(count.text()) - 1;
                    }
                    c > 0 ? count.html(c) : btn.siblings('._like').remove();
                    inProgress = false;
                })
            }
        }
        static del_post(e) {
            let btn = $(e.target).parent(); // all browsers
            if ($('._post_but_del').is(e.target)) {
                btn = $(e.target); // firefox
            }
            let id = btn.val();
            if (!inProgress) {
                Post.runAjax({"delPost": id})
                .done(data => {
                    if (data === '1') {
                        btn.closest("article").fadeOut(function() {
                            $(this).remove();
                        })
                    }
                    inProgress = false;
                });
                if (document.location.pathname !== "/") {
                    document.location.replace("/" + conf.uname);
                }
            }
        }
        getLike() {
            let count = this.likedUsers.length,
                red = `<button class='_cl_but' value='${this.id}'><img src='/static/ico/heart_red.png'></button>`,
                white = `<button class='_cl_but' value='${this.id}'><img src='/static/ico/heart_white.png'></button>`;
            if (count > 0) {
                let if_like = '';
                if ($.inArray(conf.uname, this.likedUsers) !== -1) {
                    if_like = red + `<span class='_like'>Нравится: <span class='_likecount'>${count}</span></span>`;
                } else {
                    if_like = white + `<span class='_like'>Нравится: <span class='_likecount'>${count}</span></span>`;
                }
                return if_like;
            }
            return white;
        }
        getTag() {
            let result = "";
            if (this.desc.length > 0 || this.tags.length > 0) {
                result = `<a class='_art_head_2' href='/${this.author}'>${this.author}</a> ${this.desc} `;
                $.each(this.tags, (i, tag) => {
                    result = result.concat(`<span><a href='/explore/?tag=${encodeURIComponent(tag)}'>${tag}</a></span> `);
                })
            }
            return result;
        }
        getCom() {
            let result = "",
                btn_del = "";
            $.each(this.comments, (i, data) => {
                $.each(data, (key, value) => {
                    if (conf.uname === key || conf.uname === this.author) {
                        btn_del = `<div class='_com _form_del'>
                    <button class='_com_but_del' value='${value}' title='Удалить комментарий'>
                    <img src='/static/ico/_dcom.png'></button></div>`;
                    }
                    result = result.concat(`<div class='_hdiv _com _aut_com'>
                    <a class='_art_head_2' href='${key}'>${key}</a>
                    <span> ${value}</span>${btn_del}</div>`);
                })
            })
            return result;
        }
        del_post_btn_if_author() {
            if (conf.uname === this.author) {
                return "<div class='_del_post'><div class='_com _form_del'><button class='_post_but_del' value='" +
                    this.id + "' title='Удалить публикацию'><img src='/static/ico/_dcom.png'></button></div></div>"
            }
            return '';
        }
        create() {
            // create HTML for current post
            return `<article class='_s5vjd _622au _5lms4 _8n9ix'><header class='_art_head'>
<a class='_4a6q9 _i2o1o _gvoze' href='/${this.author}/' style='width: 30px;height: 30px;'>
<img class='_rewi8' src='${conf.uploadUrl}${this.avatar}'></a><div>
<a class='_art_head_2' href='/${this.author}/'>${this.author}</a><div>${this.title}</div>
</div>${this.del_post_btn_if_author()}</header><div>
<img src='${conf.uploadUrl}${this.path}' width='600px'></div><div class='_art_foot'>
${this.getLike()}<div class='_com _aut_com'><span>${this.getTag()}</span></div>
<div><div class='_listcoms'>${this.getCom()}</div><div class='_ha6c6 _6d44r'>
<time class='_p29ma _6g6t5' title='${moment(this.createdTime).format('LL')}'>
${moment(this.createdTime).fromNow()}</time></div>
<section class='_km7ip _ti7l3'><form class='_b6i0l'>
<textarea class='_bilrf' placeholder='Добавьте комментарий...'></textarea>
<input type='button' class='_cl_bsend' value='Send'></form></section></div></article>`;

        }

    }

    class Comment {
        static hideComments() {
            let list = $('._listcoms').filter(index => index > from);
            list.each(function() {
                let item = $(this).find('._hdiv');
                let item_target = item.filter(function() {
                    return $(this).index() > 2;
                });
                let showcom = `Показать еще комментарии (${item_target.length})`;
                let link = $(`<a class='archive'>${showcom}</a>`).click(function(e) {
                    e.preventDefault();
                    item_target.toggle(this);
                    if ($(e.target).text() === showcom) {
                        $(this).text("Скрыть комментарии");
                    } else {
                        $(this).text(showcom);
                    }
                });
                item_target.hide().eq(0).before(link);
            })
        }
        static add_comment(e) {
            let btn = $(e.target),
                com = $(this).siblings('._bilrf').val(),
                id = $(this).closest("._art_foot").find('._cl_but').val();
            if (com.trim() && !inProgress) {
                Post.runAjax({"comId": id, "addCom": com})
                .done(data => {
                    if (data === '1') {
                        $(e.target).siblings('._bilrf').val('').height(18);
                        let btn_del = `<div class='_com _form_del'>
        <button class='_com_but_del' value='${com}' title='Удалить комментарий'>
        <img src='/static/ico/_dcom.png'></button></div>`;
                        btn.closest("._art_foot").find("._listcoms").append(
        `<div class='_hdiv _com _aut_com'>
        <a class='_art_head_2' href='/${conf.uname}/'>${conf.uname}</a>
        <span> ${com}</span>${btn_del}</div>`);
                    }
                    inProgress = false;
                })
            }
        }
        static del_comment(e) {
            let btn = $(e.target).parent(); // all browsers
            if ($('._com_but_del').is(e.target)) {
                btn = $(e.target); // firefox
            }
            let com = btn.val(),
                id = $(this).closest("._art_foot").find('._cl_but').val();
            if (!inProgress) {
                Post.runAjax({"imgId": id, "delCom": com})
                .done(data => {
                    if (data === '1') {
                        btn.closest("div._hdiv").fadeOut(function() {
                            $(this).remove();
                        })
                    }
                    inProgress = false;
                })
            }
        }
    }


    Comment.hideComments();
    html.on('click', '._cl_but', Post.like);
    html.on('click', '._post_but_del', Post.del_post);
    html.on('click', '._com_but_del', Comment.del_comment);
    html.on('click', '._cl_bsend', Comment.add_comment);
    html.on('keyup', 'textarea', function() {
        $(this).height(18);
        $(this).height(this.scrollHeight);
    });

    if (window.location.pathname === '/') {
    $(window).scroll(function() {
    /* Если высота окна + высота прокрутки больше или равны высоте всего документа
    и ajax-запрос в настоящий момент не выполняется, то запускаем ajax-запрос */
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 200 && !inProgress){
    $.ajax({
        url: '/',
        type: 'POST',
        data: {"startFrom": startFrom},
        beforeSend: () => {
            inProgress = true;
            $("#loader").css("display", "block").animate({"opacity": 1}, 500);
        }
        }).done(data => {
        data = JSON.parse(data);
        $("#loader").animate({"opacity": 0}, 500, function(){
            $("#loader").css("display", "");
        });
        if (data.length > 0) {
            $.each(data, (index, img) => {
                let post = new Post(img);
                let article = post.create();
                $("#articles").append(article);
                inProgress = false;
                startFrom = img._id.$oid;
            });
            from += conf.numPerPage;
            Comment.hideComments();
        }})
    }
    })
    }

})(jQuery);