$(document).ready(function(){
	var ctrl_sidebar = '.ctrl-sidebar';
	var ctrl_setting = '.setting';
	var sleep_mode = 'off';
	var overload = '.overload';
	var close_nav = '#close-nav-bar';
	var delay = 400;
	var showSidebar = function(show){
		if(show){
			$('.sidebar').animate({left: 0}, delay, function(){$(overload).addClass('in');});
			$(overload).fadeIn(delay);
		}
		else{
			$('.sidebar').animate({left: -240}, delay, function(){$(overload).removeClass('in');});
			$(overload).fadeOut(delay);
		}
		
	};
	$([ctrl_sidebar,overload,close_nav].join(',')).on('click', function(event){
		event.preventDefault();
		if($(overload).hasClass('in')){
			showSidebar(false);
		}
		else{
			showSidebar(true);
			$(overload).attr('act-func',$(ctrl_sidebar).attr('act-func'));
		}
	});

	var showSetting = function(show){
		if(show){
			$('#setting').slideDown(delay, function(){$(overload).addClass('in');});
		}
		else{
			$('#setting').slideUp(delay, function(){$(overload).removeClass('in');});
		}
		
	};
	$([ctrl_setting, overload, '#setting-close'].join(',')).on('click', function(event){
		event.preventDefault();
		if($(overload).hasClass('in')){
			showSetting(false);
		}
		else{
			showSetting(true);
			$(overload).attr('act-func',$(ctrl_setting).attr('act-func'));
		}
	});

	$([ctrl_setting, overload, ctrl_sidebar].join(',')).on('click', function(event){
		event.preventDefault();
		if($(overload).hasClass('in')){
			eval($(overload).attr('act-func')+'(false)');
		}
	});

	$('#default_sleep_mode').on('click', function(){
		if($('#default_sleep_mode').attr('current') != 'on'){
			$(this).attr('current', 'on');
			sleepMode('on');
		}else{
			$(this).attr('current', 'off');
			sleepMode('off');
		}
	});

	var submitFont = function(size){
		$('#chapter-content').css({'font-size': size});
		$('li.font-val').removeClass('active');
		$('li.font-val.size-' + size).addClass('active');
		$('.current').text($('li.font-val.size-' + size).text());
	};

	if ( readPage != undefined){
		if ( $.cookie('sleepmode') ){
			sleep_mode = 'on';
			$('#sleepmode_btn').attr('checked', 'checked');
			$('#default_sleep_mode').attr('current', 'on');
		}
		if ( $.cookie('fontsize') ){
			submitFont($.cookie('fontsize'));
		}
	}
	var sleepMode = function(sleep_mode){
		if(sleep_mode == 'on'){
			$('#sleep-mode').fadeIn(700);
			$.cookie('sleepmode', 1, { expires: 0.2, path: '/' });
		}else{
			$('#sleep-mode').fadeOut(700);
			if(readPage != undefined){
				$.cookie('sleepmode', 0, { expires: 0, path: '/' });
			}
		}
	};
	sleepMode(sleep_mode);


	var selectFont = function(show){
		if(show){
			$('.font-select,.setting-overload').addClass('in');
		}else{
			$('.font-select,.setting-overload').removeClass('in');
		}
	};
	$('.font-size').on('click', function(){
		selectFont(true);
	});
	$('.setting-overload').on('click', function(){
		selectFont(false);
	});
	$('.font-val').on('click', function(){
		$('.font-val').removeClass('active');
		var size = $(this).attr('val');
		submitFont(size);
		selectFont(false);
		$.cookie('fontsize', size, { expires: 1, path: '/' });
	});

});

/*
# 
# Hide Header on on scroll down
# 
*/
var didScroll;
var lastScrollTop = 0;
var delta = 5;
var navbarHeight = $('#header.fixed').outerHeight();

$(window).scroll(function(event){
	didScroll = true;
});

setInterval(function() {
	if (didScroll) {
		hasScrolled();
		didScroll = false;
	}
}, 150);

function hasScrolled() {
	var st = $(this).scrollTop();
	if(Math.abs(lastScrollTop - st) <= delta)
		return;

	if (st > lastScrollTop && st > navbarHeight){
		$('#header.fixed').removeClass('nav-down').addClass('nav-up');
		$('#scroll-top').removeClass('hide');
		$('.control-panel').removeClass('in')
	} else {
		if(st + $(window).height() > $(document).height()) {
			$('#header.fixed').removeClass('nav-up').addClass('nav-down');
			$('.control-panel').addClass('in');
		}
	}
	if(st < 100)
	{
		$('#scroll-top').addClass('hide')
	}
	lastScrollTop = st;
};
/*
# END Hide Header on on scroll down
 */

$('#scroll-top').click(function(){
    $('html').animate({scrollTop:0}, 'slow');
    $('body').animate({scrollTop:0}, 'slow');
    $('.popupPeriod').fadeIn(1000, function(){
        setTimeout(function(){$('.popupPeriod').fadeOut(2000);}, 3000);
    });
});



function debounce(fn, delay) {
	var timer = null;
	return function () {
		var context = this, args = arguments;
		clearTimeout(timer);
		timer = setTimeout(function () {
			fn.apply(context, args);
		}, delay);
	};
};

var search = function(val){

	$.ajax({
		url: 	'/tim-kiem?k=' + val, 
		type: 	'get',  
		contentType: 	false,
		cache: 			false,
		dataType: 		"json",
		processData: 	false,   
		success: function(data) {
			renderData(data,val);
        },
		error: function(data) {
			renderData([], false);
        },
	});
};

$(document).ready(function(){
	$('#key-search').focus(function(){
		$('#complete').fadeIn(150);
	}).focusout(function(){
		$('#complete').fadeOut(150);
	});
	$('#key-search').keyup(debounce(function(){
		var val = $(this).val();
		if(val == '' || val === undefined || val.length < 4){
			return;
		}else{
			search(val);
		}
		
	}, 100));

	$('#form-search').submit(function(event){
		var val = $('#key-search').val();
		event.preventDefault();
		if(val == '' || val === undefined || val.length < 4){
			return;
		}else{
			search(val);
		}
	});
	$('#submit-search').on('click', function(){
		if(!$(this).hasClass('in')){
			$('#key-search').focus();
			$(this).addClass('in');
			$('.nav-search').addClass('in');
			return false;
		}else{
			$('#complete').fadeOut(150);
			$(this).removeClass('in');
			$('.nav-search').removeClass('in');
		}
	});
});
var renderData = function(data, val){
	$('#group-mangas,#group-authors,#not-found').empty();
	mangas = data.result;
	if(mangas.length > 0){
		$('#not-found').fadeOut();
		$('#group-mangas').fadeIn(150);
		for (var i = 0; i < mangas.length; i++) {
			var name = mangas[i].title.trim();
			var keys = val.trim().split(' ');
			keys.forEach(function(key, index){
				name = name.replace(key.capitalize(), '<b>'+key.capitalize()+'</b>');
			});
			var href = $('<a href="/truyen/' + mangas[i].slug +'.html" class="link-cate"  title="Truyện '+name+'">'+ name +' <span class="view-count-search"><span class="fa fa-eye"></span> '+ mangas[i].view +'</span></a>');
			var item = $('<li class="item"></li>').append(href);
			$('#group-mangas').append(item);
		}
	}else{
		$('#not-found').fadeIn().append($('<li class="not-found"><a href="javascript: -1">Không tìm thấy kết quả</a></a></li>'));
		$('#group-mangas').empty().fadeOut(150);
	}
};

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

$('a.link-cate').on('click', function(event){
	event.preventDefault();
	window.location.href=$(this).attr('href');
});
/*
#
# V2 - Group by manga or author
#
var renderData = function(result){
	$('#group-mangas,#group-authors,#not-found').empty();
	if(result.count != 0){
		$('#not-found').fadeOut();
		mangas = result.mangas
		authors = result.authors
		if(mangas.length > 0){
			$('#group-mangas').fadeIn(150).append($('<li class="title"><a href="">Truyện</a></li>'));
			for (var i = 0; i < mangas.length; i++) {
				var item = $('<li class="item"><a href="">'+ mangas[i].name +' <span class="view-count-search"><span class="fa fa-eye"></span> '+ mangas[i].view +'</span></a></li>');
				$('#group-mangas').append(item)
			}
		}else{
			$('#group-mangas').empty().fadeOut(150)
		}
		if(authors.length > 0){
			$('#group-authors').fadeIn(150).append($('<li class="title"><a href="">Tác gỉa</a></li>'));
			for (var i = 0; i < authors.length; i++) {
				var item = $('<li class="item"><a href="">'+ authors[i].name +'</span></a></li>');
				$('#group-authors').append(item)
			}
		}else{
			$('#group-authors').empty().fadeOut(150);
		}
	}else{
		$('#not-found').fadeIn().append($('<li class="not-found"><a href="javascript: -1">Không tìm thấy kết quả</a></a></li>'));
	}
}*/

/*
#
# Init on load
#
 */