window.redblock = function (search_str){
    var s = search_str;
    $(".reddiv").css({'border':'2px solid #F00'});
    $('a').each( function () {
        var regx=new RegExp(s,"g");
        if(regx.test($(this).text())){
	    //$(this).css('background-color', 'yellow');
            $(this).css('border','3px solid red');
        }
    }); null
};

window.redblock_g = function (search_str,reg){
    var s = search_str;
    var checkget = false; 
    $('.g').each( function () {
        var regs=new RegExp(s,"g");
        var regurl=new RegExp(reg,"g");
        if(regs.test($('h3',$(this)).text()) && regurl.test($('cite',$(this)).text())){ 
            $('h3',$(this)).css('border','3px solid red');
            checkget = true;
        }
    });
    return checkget;
};

