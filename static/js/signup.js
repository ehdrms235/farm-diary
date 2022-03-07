function openPopup2(url) {
	 
    var _width = '650';
    var _height = '900';
 
    // 팝업을 가운데 위치시키기 위해 아래와 같이 값 구하기
    var _left = Math.ceil(( window.screen.width - _width )/2);
    var _top = Math.ceil(( window.screen.height - _height )/2); 
 
    window.open(url, 'popup-test', 'width='+ _width +', height='+ _height +', left=' + _left + ', top='+ _top );
 
}