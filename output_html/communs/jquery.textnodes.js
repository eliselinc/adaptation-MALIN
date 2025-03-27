$.fn.textNodes = function()
{
	return $(this).contents().filter(function(){ return this.nodeType == 3 || this.nodeName == "BR" ; });
}
