$(document).ready(function(){
    $('#like_button').click(function(e){
        e.preventDefault();
        var recipe_id = $(this).attr('recipe_id');

        $.get('/ajax_like/',{ recipe_id : recipe_id},'json')
            .done(function() {

                num_likes = parseInt($('#num_likes').text());
                if($('#like_button').text() == 'Like')
                {
                    $('#like_button').text('Unlike');
                    $('#num_likes').text((num_likes + 1));
//                    alert(String.fromCharCode(num_likes + 1));
                }
                else
                {
                    $('#like_button').text('Like');
                    $('#num_likes').text((num_likes - 1));

                }
            });
    });
});

$('#like_button').ready(function(){
    $()
});
