$(document).ready(function() {
$.post('/ajax_/', function(data) {
conf = JSON.parse(data);
})

var inProgress = false,
    inProgress2 = false,
    startFrom = $("._cl_but:last")[0].value,
    from = -1;

hideComments();
$('html').on('click','._cl_but', like);
$('html').on('click','._post_but_del', del_post);
$('html').on('click','._com_but_del', del_comment);
$('html').on('click','._cl_bsend', add_comment);
$('html').on('keyup','textarea', function() {
   $(this).height(18);
   $(this).height(this.scrollHeight);
})

if (window.location.pathname === '/') {
$(window).scroll(function() {
    /* Если высота окна + высота прокрутки больше или равны высоте всего документа
    и ajax-запрос в настоящий момент не выполняется, то запускаем ajax-запрос */
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 200 && !inProgress){
    $.ajax({
        url: '/',
        type: 'POST',
        data: {"startFrom" : startFrom},
        beforeSend: function(){
            inProgress = true;
            $("#loader").css("display", "block");
            $("#loader").animate({"opacity": 1}, 500);
        }
        }).done(function(data){
        var data = JSON.parse(data);
        $("#loader").animate({"opacity": 0}, 500, function(){
            $("#loader").css("display", "");
        });
        if (data.length > 0) {
            $.each(data, function(index, img) {
            var article = "<article class='_s5vjd _622au _5lms4 _8n9ix'>\
<header class='_art_head'><a class='_4a6q9 _i2o1o _gvoze' href='/"+img.author.name+
"/' style='width: 30px;height: 30px;'><img class='_rewi8' src='"+conf.uploadUrl+
img.author.avatar+"'></a><div><a class='_art_head_2' href='/"+img.author.name+"/'>"+
img.author.name+"</a><div>"+img.title+"</div></div>"+
del_post_btn_if_author(img.author.name, img._id.$oid)+"</header><div><img src='"+conf.uploadUrl+
img.path+"' width='600px'></div><div class='_art_foot'>"+getLike(img.liked_users, img._id.$oid)+
"<div class='_com _aut_com'><span>"+getTag(img.author.name, img.description, img.tags)+
"</span></div><div><div class='_listcoms'>"+getCom(img.comments, img.author.name)+
"</div><div class='_ha6c6 _6d44r'><time class='_p29ma _6g6t5' title='"+
moment(img.created_time.$date).format('LL')+"'>"+moment(img.created_time.$date).fromNow()+
"</time></div><section class='_km7ip _ti7l3'><form class='_b6i0l'>\
<textarea class='_bilrf' placeholder='Добавьте комментарий...'></textarea>\
<input type='button' class='_cl_bsend' value='Send'></form></section></div></article>";

            $("#articles").append(article);
            inProgress = false;
            startFrom = img._id.$oid;
            })
            from += conf.numPerPage;
            // console.log('from: ',from);
            hideComments();
        }})
    }
})
}


function getTag(author, desc, tags) {
var result = "";
if (desc.length > 0 || tags.length > 0) {
    result = "<a class='_art_head_2' href='/"+author+"'>"+author+"</a> "+desc+" ";
    $.each(tags, function(i, tag) {
    result = result.concat("<span><a href='/explore/?tag="+encodeURIComponent(tag)+"'>"+tag+"</a></span> ");
    })
}
return result;
}

function getCom(comments, author) {
var result = "";
for (let data in comments) {
    var item = comments[data];
    for (var key in item) {
        var value = item[key];
        if (conf.uname === key || conf.uname === author) {
            var btn_del = "<div class='_com _form_del'><button class='_com_but_del' value='"+
        value+"' title='Удалить комментарий'><img src='/static/ico/_dcom.png'></button></div>";
        } else {
            var btn_del = '';
        }
        result = result.concat("<div class='_hdiv _com _aut_com'><a class='_art_head_2' href='/user/"+
            key+"'>"+key+"</a><span> "+value+"</span>"+btn_del+"</div>");
    }
}
return result;
}

function getLike(liked_users, id) {
let count = liked_users.length,
    red = "<button class='_cl_but' value='"+id+"'><img src='/static/ico/heart_red.png'></button>",
    white = "<button class='_cl_but' value='"+id+"'><img src='/static/ico/heart_white.png'></button>";
if (count > 0) {
    if ($.inArray(conf.uname, liked_users) != -1) {
        if_like = red + "<span class='_like'>Нравится: <span class='_likecount'>"+count+"</span></span>";
    } else {
        if_like = white + "<span class='_like'>Нравится: <span class='_likecount'>"+count+"</span></span>";
    }
    return if_like;
}
return white;
}

function hideComments() {
var list = $('._listcoms').filter(function(index) {
    return index > from;
    })
list.each(function() {
var item = $(this).find('._hdiv'),
    item_target = item.filter(function() {
    return $(this).index() > 2;
    })
var showcom = "Показать еще комментарии ("+item_target.length+")";
var link = $('<a class="archive">'+showcom+'</a>').click(function(e) {
e.preventDefault();
item_target.toggle(this);
if ($(e.target).text() === showcom) {
    $(this).text("Скрыть комментарии");
} else {
    $(this).text(showcom);
}
})
item_target.hide().eq(0).before(link);
})
}

function add_comment(e) {
let btn = $(e.target),
    com = $(this).siblings('._bilrf').val(),
    id = $(this).closest(
        "._art_foot").find('._cl_but').val();
if (com.trim() && !inProgress2) {
$.ajax({
    url: '/ajax_/',
    type: 'POST',
    data: {"comId": id, "addCom": com},
    beforeSend: function(){
    inProgress2 = true;}
    }).done(function(data){  
    if (data === '1') {
    $(e.target).siblings('._bilrf').val('').height(18);
    let btn_del = "<div class='_com _form_del'><button class='_com_but_del' value='"+
        com+"' title='Удалить комментарий'><img src='/static/ico/_dcom.png'></button></div>";
    btn.closest("._art_foot").find("._listcoms").append(
        "<div class='_hdiv _com _aut_com'><a class='_art_head_2' href='/"+conf.uname+
        "/'>"+conf.uname+"</a><span> "+com+"</span>"+btn_del+"</div>");
    }
    inProgress2 = false;
    })
}
}

function like(e) {
var id = $(this).val();
if (!inProgress2) {
$.ajax({
    url: '/ajax_/',
    type: 'POST',
    data: {"like" : id},
    beforeSend: function(){
    inProgress2 = true;}
    }).done(function(data){
    let btn = $(e.target).parent(); // all browsers
    if ( $('._cl_but').is(e.target) ) {
        btn = $(e.target);          // firefox
    }
    let count = btn.siblings('._like').find($("._likecount")),
    c;
if (data === '1') {
    $("img", btn).attr("src","/static/ico/heart_red.png");
    if (count.length === 1) {
    c = parseInt(count.text()) + 1;
    } else {
    btn.after("<span class='_like'>Нравится: <span class='_likecount'>1</span></span>");
    c = 1;
    }
} else {
    $("img", btn).attr("src","/static/ico/heart_white.png");
    c = parseInt(count.text()) - 1;
}
if (c > 0){
    count.html(c);
} else {
    btn.siblings('._like').remove();
}
inProgress2 = false;
})
}
}

function del_post_btn_if_author(author, id) {
if (conf.uname === author) {
    return "<div class='_del_post'><div class='_com _form_del'><button class='_post_but_del' value='"+
    id+"' title='Удалить публикацию'><img src='/static/ico/_dcom.png'></button></div></div>";
}
return '';
}

function del_post(e) {
let btn = $(e.target).parent(); // all browsers
if ( $('._post_but_del').is(e.target) ) {
    btn = $(e.target);          // firefox
}
let id = btn.val();
if (!inProgress2) {
$.ajax({
    url: '/ajax_/',
    type: 'POST',
    data: {"delPost": id},
    beforeSend: function(){
    inProgress2 = true;}
    }).done(function(data){
    if (data === '1') {
    btn.closest("article").fadeOut(function(){
        $(this).remove();
    })}
    inProgress2 = false;
    })
if (document.location.pathname != "/") {
    document.location.replace("/" + conf.uname);
}
}
}

function del_comment(e) {
let btn = $(e.target).parent(); // all browsers
if ( $('._com_but_del').is(e.target) ) {
    btn = $(e.target);          // firefox
}
let com = btn.val(),
    id = $(this).closest(
    "._art_foot").find('._cl_but').val();
if (!inProgress2) {
$.ajax({
    url: '/ajax_/',
    type: 'POST',
    data: {"imgId": id, "delCom": com},
    beforeSend: function(){
    inProgress2 = true;}
    }).done(function(data){
    if (data === '1') {
    btn.closest("div._hdiv").fadeOut(function(){
        $(this).remove();
    })}
    inProgress2 = false;
    })
}
}

})