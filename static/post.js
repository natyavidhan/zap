function refresh_comments(post) {
    $.ajax({
        type: 'GET',
        url: `/post/${post}?json=True`,
        success: function(msg){
            $(".comment-list").empty();
            msg['post']['comments'].forEach(element => {
                console.log(element);
                $(".comment-list").append(
                    `<li><a href="/profile/${element['userid']}">${element['username']}</a>: ${element['comment']}</li>`
                )
            });
            console.log(msg);
        }
    });
}

function comment(post) {
    let comment = document.querySelector("input[name='comment']").value;
    $.ajax({
        type: 'POST',
        url: `/comment?post=${post}&comment=${comment}`,
        success: function(msg){
            if (msg == "True") {
                refresh_comments(post);
            }
        }
    });
}

function like(post) {
    $.ajax({
        type: 'POST',
        url: `/like?post=${post}`,
        success: function(msg){
            if (msg == "True") {
                let btn = $(`[data-post-id="${post}"] > div.stats > button[name="like-btn"]`);
                let count = parseInt(btn.text());
                if (btn.hasClass("btn-light")){
                    btn.removeClass("btn-light");
                    btn.addClass("btn-outline-light");
                    count-=1;
                    btn.html(`<i class="bi bi-heart"></i> ${count}`);
                } else {
                    btn.addClass("btn-light");
                    btn.removeClass("btn-outline-light");
                    count+=1;
                    btn.html(`<i class="bi bi-heart-fill"></i> ${count}`);
                }
            }
        }
    });
}