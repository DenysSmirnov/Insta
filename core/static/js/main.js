$(document).ready(function(){
var host = window.location.hostname;
if (host === '127.0.0.1'){
    path = '/static/upload/resized-images/';
} else {
    path = 'https://s3.us-east-2.amazonaws.com/insta-s3-bucket/upload/';
};
$.post('/ajax_/', onSuccess);
    function onSuccess(data){
    conf = JSON.parse(data);
    };
var inProgress = false;
var startFrom = $("._cl_but:last")[0].value;


function getTag(author, desc, tags){
var result = "";
if (desc.length > 0 || tags.length > 0){
    result = "<a class='_art_head_2' href='/"+author+"'>"+author+"</a> "+desc+" ";
    $.each(tags, function(i, tag){
    result = result.concat("<span><a href='/explore/?tag="+encodeURIComponent(tag)+"'>"+tag+"</a></span> ");
    });
    };
return result;
};    


function getCom(comments, author){
var result = "";
for (var data in comments){
    var item = comments[data];
    for (var key in item){
        var value = item[key];
        if (conf['uname'] === key || conf['uname'] === author){
            var btn_del = "<div class='_com _form_del'><button class='_com_but_del' value='"+
        value+"' title='Удалить публикацию'><img src='/static/ico/_dcom.png'></button></div>";
        } else {
            var btn_del = '';
        };
        result = result.concat("<div class='_hdiv _com _aut_com'><a class='_art_head_2' href='/user/"+
            key+"'>"+key+"</a><span> "+value+"</span>"+btn_del+"</div>")
    };
};
return result;
};


function getLike(liked_users, id){
let count = liked_users.length;
let red = "<button class='_cl_but' value='"+id+"'><img src='/static/ico/heart_red.png'></button>";
let white = "<button class='_cl_but' value='"+id+"'><img src='/static/ico/heart_white.png'></button>";
if(count>0){
    if ($.inArray(conf['uname'], liked_users) != -1){
        if_like = red + "<span class='_like'>Нравится: <span class='_likecount'>"+count+"</span></span>";
    } else {
        if_like = white + "<span class='_like'>Нравится: <span class='_likecount'>"+count+"</span></span>";
    };
    return if_like;
} else {
    return white;
}
};


var from = -1;
function hideComments(){
var list = $('._listcoms').filter(function(index){
    return index > from
    });
list.each(function(){
var item = $(this).find('._hdiv'),
    item_target = item.filter(function(){
    return $(this).index() > 2
    });
    // console.log(item_target);
var showcom = "Показать еще комментарии ("+item_target.length+")";
var link = $('<a class="archive">'+showcom+'</a>').click(function(e){
e.preventDefault();
item_target.toggle(this);
if ($(e.target).text() === showcom){
    $(this).text("Скрыть комментарии");
} else {
    $(this).text(showcom);
}
});
item_target.hide().eq(0).before(link);
});
};
hideComments(); 


function like(e){
let id = $(this).parent()[0].value;
if (!inProgress){
$.ajax({
    url: '/',
    method: 'POST',
    data: {"like" : id},
    beforeSend: function(){
    inProgress = true;}
    }).done(function(data){
// console.log('передано: ', id);
let btn = $(e.target).parent();
let count = btn.siblings('span').find($("._likecount"));
let c;
if (data === '1'){
    $("img", btn).attr("src","/static/ico/heart_red.png");
    if (count.length === 1){
    c = parseInt(count.text()) + 1;
    } else {
    btn.after("<span class='_like'>Нравится: <span class='_likecount'>1</span></span>");
    c = 1;
    };
} else {
    $("img", btn).attr("src","/static/ico/heart_white.png");
    c = parseInt(count.text()) - 1;
};
if (c > 0){
    count.html(c);
} else {
    btn.siblings('span').detach();
};
inProgress = false;
});
};
};
$('._cl_but img').on('click', like);


function del_post_btn_if_author(author, id){
    if (conf['uname'] === author){
        return "<div class='_del_post'><div class='_com _form_del'><button class='_post_but_del' value='"+
        id+"' title='Удалить публикацию'><img src='/static/ico/_dcom.png'></button></div></div>";
    } else {
        return '';
    }
};


function del_post(e){
let btn = $(e.target).parent();
let id = btn[0].value;
if (!inProgress){
$.ajax({
    url: '/ajax_/',
    method: 'POST',
    data: {delPost: id},
    beforeSend: function(){
    inProgress = true;}
    }).done(function(data){
    if (data === '1'){
    btn.closest("article").fadeOut(
        function(){$(this).remove()
    }); 
    };
    inProgress = false;
    });
};
};  
$('._post_but_del img').on('click', del_post);


function del_comment(e){
let btn = $(e.target).parent();
let com = btn[0].value;
let id = $(this).closest(
    "._art_foot").find('._cl_but')[0].value;
if (!inProgress){
$.ajax({
    url: '/ajax_/',
    method: 'POST',
    data: {delCom: com, imgId: id},
    beforeSend: function(){
    inProgress = true;}
    }).done(function(data){
    if (data === '1'){
    btn.closest("div._hdiv").fadeOut(
        function(){$(this).remove()
    });
    };
    inProgress = false;
    });
};
};  
$('._com_but_del img').on('click', del_comment);


$('textarea').keyup(function(){
   $(this).height(18);
   $(this).height(this.scrollHeight);
});


if (window.location.pathname === '/'){
$(window).scroll(function(){
    /* Если высота окна + высота прокрутки больше или равны высоте всего документа и ajax-запрос в настоящий момент не выполняется, то запускаем ajax-запрос */
    if($(window).scrollTop() + $(window).height() >= $(document).height() - 200 && !inProgress){
    
    $.ajax({
        url: '/',
        method: 'POST',
        data: {"startFrom" : startFrom},
        beforeSend: function(){
        inProgress = true;}
        }).done(function(data){
    console.log(startFrom);
        img = JSON.parse(data);
        if (img.length > 0){
            $.each(img, function(index, img){
            var articles = "<article class='_s5vjd _622au _5lms4 _8n9ix'><header class='_art_head'><a class='_4a6q9 _i2o1o _gvoze' href='/"+img.author.name+"/' style='width: 30px;height: 30px;'><img class='_rewi8' src='"+path+img.author.avatar+
"'></a><div><a class='_art_head_2' href='/"+img.author.name+"/'>"+img.author.name+"</a><div>"+img.title+"</div></div>"+del_post_btn_if_author(img.author.name, img._id.$oid)+"</header><div><img src='"+path+img.path+"' width='600px'></div><div class='_art_foot'>"+
getLike(img.liked_users, img._id.$oid)+"<div class='_com _aut_com'><span>"+getTag(img.author.name, img.description, img.tags)+"</span></div><div><div class='_listcoms'>"+
getCom(img.comments, img.author.name)+"</div><div class='_ha6c6 _6d44r'><time class='_p29ma _6g6t5' title='"+moment(img.created_time.$date).format('LL')+"'>"+moment(img.created_time.$date).fromNow()+
"</time></div><section class='_km7ip _ti7l3'><form class='_b6i0l' method='POST'><textarea class='_bilrf' name='comment' placeholder='Добавьте комментарий...'></textarea><input type='submit' class='cl_bsend' value='Send'><input type='hidden' name='id' value='"+
img._id.$oid+"'></form></section></div></article>";

            $("#articles").append(articles);
            inProgress = false;
            startFrom = img._id.$oid;
            });
            from += conf['numPerPage'];
            // console.log('from: ',from);
            hideComments();
            $('._cl_but img').on('click', like);
            $('._post_but_del img').on('click', del_post);
            $('._com_but_del img').on('click', del_comment);
            $('textarea').keyup(function(){
                $(this).height(18);
                $(this).height(this.scrollHeight);
            });
        }});
    };
});
};
});