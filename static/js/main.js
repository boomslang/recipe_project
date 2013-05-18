$(document).ready(function(){
    $('#like_button').click(function(e){
        e.preventDefault();
        var recipe_id = $(this).attr('recipe_id');

        $.get('/ajax_like/',{ recipe_id : recipe_id},'json')
            .done(function() {

                if($('#like_button').text() == 'Like')
                {
                    $('#like_button').text('Unlike');
                }
                else
                {
                    $('#like_button').text('Like');
                }
            });
    });
});

$('#like_button').ready(function(){
    $()
});
