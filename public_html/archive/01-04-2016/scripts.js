var lastMenuItem = null;

function overMenuItem(menuItem)
{
	menuItem.style.background="#202020";
	menuItem.style.color="#d0d0d0";
	document.getElementById(menuItem.id.concat("_menu_bar")).style.display="block";
	if (lastMenuItem != null && lastMenuItem != menuItem)
	{
		lastMenuItem.style.background="#d0d0d0";
		lastMenuItem.style.color="#000000";
		document.getElementById(lastMenuItem.id.concat("_menu_bar")).style.display="none";
	}
	lastMenuItem = menuItem;
}