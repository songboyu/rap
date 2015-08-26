function redblock(search_str){
    var s = search_str;
    $(".reddiv").css({'border':'2px solid #F00'});
    $('a').each( function () {
        var regx=new RegExp(s,"g");
        if(regx.test($(this).text())){
	    //$(this).css('background-color', 'yellow');
            $(this).css('border','3px solid red')
        }
    }); null
}

