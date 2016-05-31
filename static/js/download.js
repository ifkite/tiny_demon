requirejs(['./common', 'lib/jquery'], function(common, jquery){
    $(
        function(){
            $('a').each(function(){$(this).text(unescape($(this).text()))});
        }
    )
});
