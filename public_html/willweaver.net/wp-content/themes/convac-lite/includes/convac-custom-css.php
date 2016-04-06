<?php 
	
	function convac_lite_Hex2RGB($hexStr, $returnAsString = false, $seperator = ',') {
		$hexStr = preg_replace("/[^0-9A-Fa-f]/", '', $hexStr); // Gets a proper hex string
		$rgbArray = array();
		if (strlen($hexStr) == 6) { //If a proper hex code, convert using bitwise operation. No overhead... faster
			$colorVal = hexdec($hexStr);
			$rgbArray['red'] = 0xFF & ($colorVal >> 0x10);
			$rgbArray['green'] = 0xFF & ($colorVal >> 0x8);
			$rgbArray['blue'] = 0xFF & $colorVal;
		} elseif (strlen($hexStr) == 3) { //if shorthand notation, need some string manipulations
			$rgbArray['red'] = hexdec(str_repeat(substr($hexStr, 0, 1), 2));
			$rgbArray['green'] = hexdec(str_repeat(substr($hexStr, 1, 1), 2));
			$rgbArray['blue'] = hexdec(str_repeat(substr($hexStr, 2, 1), 2));
		} else {
			return false; //Invalid hex color code
		}
		return $returnAsString ? implode($seperator, $rgbArray) : $rgbArray; // returns the rgb string or the associative array
	}
	
	$_contact_header_type = '';
	
	$bg_color = get_theme_mod('_colorpicker', '#f65e13');
	$fullparallax_image = get_theme_mod('_fullparallax_image', '');
	$innerheader_image = get_theme_mod('_innerheader_stype', '');
	$_footer_strip_bg = get_theme_mod('_footer_strip_bg', '');
	$_iconcolorpicker = get_theme_mod('_iconcolorpicker', '');
	$_persistent_on_off = get_theme_mod('_persistent_on_off', '');
	$_innerpage_img = get_theme_mod('_innerpage_img', '');

	$rgb=array();
	$rgb = convac_lite_Hex2RGB($bg_color);
	$R = $rgb['red'];
	$G = $rgb['green'];
	$B = $rgb['blue'];

	$rgbcolor = "rgba(". $R .",". $G .",". $B .",.4)";
	$sktgbcolor = "rgba(". $R .",". $G .",". $B .",.2)";
	$sktgbcolor2 = "rgba(". $R .",". $G .",". $B .",.1)";
	$bdrrgbcolor = "rgba(". $R .",". $G .",". $B .",.6)";
	$navrgbcolor = "rgba(". $R .",". $G .",". $B .",.8)";

	
	$_moblie_menu = get_theme_mod('_moblie_menu', '');
	$_moblie_menu = ($_moblie_menu) ? $_moblie_menu : '1024';
	
	$_res_font_color = get_theme_mod('_res_font_color', '');
	$_res_bgcolor = get_theme_mod('_res_bgcolor', '');
	
	$_home_map_overlayimg = get_theme_mod('_home_map_overlayimg', '');

?>

<style type="text/css">

	/***************** THEME *****************/
	.res-button{color: <?php if(isset($_res_font_color )){ echo $_res_font_color ; } ?>;background:<?php if(isset($_res_bgcolor )){ echo $_res_bgcolor; } ?>;}
	.res-button:hover{background: <?php if(isset($_res_font_color )){ echo $_res_font_color ; } ?>;color:<?php if(isset($_res_bgcolor )){ echo $_res_bgcolor; } ?>;}
	.bread-title-holder,.teamsocial li a,.skepost-meta > span,#wp-calendar tbody a{ background: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	.skt-opening-hours-widget .opening-hours-list li:hover {border-top-color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>; }
	.service-icon:before {border-bottom-color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>; }
	h1, h2, h3, h4, h5, h6,.food_map_window .food_right_sec h3,.contact_form_title,#contact_page_temp .contact_top_block h3,blockquote.sketch-quote a,.quoteauthor a,blockquote,.widget_tag_cloud a{color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	.error404 #searchform input[type="text"]:focus, .search #searchform input[type="text"]:focus, #sidebar #searchform input[type="text"]:focus, #footer #searchform input[type="text"]:focus,#wp-calendar {border-color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}	
	li.ui-timepicker-selected, .ui-timepicker-list li:hover, .ui-timepicker-list .ui-timepicker-selected:hover,#wp-calendar thead{background: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}	
	.sticky-post {color : <?php if(isset($bg_color)){ echo $bg_color; } ?>;border-color:<?php if(isset($bdrrgbcolor)){ echo $bdrrgbcolor; } else { echo '#f65e13'; } ?>}
	#footer,.skt-opening-hours-widget .opening-hours-list li.active{ border-color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>; }
	.social li a:hover,.skt-opening-hours-widget .opening-hours-list li:hover,.skt-opening-hours-widget .opening-hours-list li.active,#about_author_box .author_social li a,.sketch_price_table .price_table_inner ul li.table_title{background: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	.social li a:hover:before{color:#fff; }
	a#backtop,#respond input[type="submit"],.skt-ctabox div.skt-ctabox-button a:hover,.continue a,#convac-paginate .convac-current,#convac-paginate a:hover,.comments-template .reply a,#commentsbox .reply a,#content .contact-left form input[type="submit"]:hover,.skt-parallax-button:hover,.sktmenu-toggle,#footer .tagcloud a:hover,._404_artbg img,.full-map-box .hsearch-close,form input[type="submit"],.widget_tag_cloud a:hover {background-color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>; }
	form.wpcf7-form input[type="submit"],#convac_lite_reservation input[type="submit"],.postformat-gallerycontrol-nav a.postformat-galleryactive,.skt-rate-price{background-color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>; }
	.skt-ctabox div.skt-ctabox-button a,#portfolio-division-box .readmore,.teammember,.slider-link a,.ske_tab_v ul.ske_tabs li.active,.ske_tab_h ul.ske_tabs li.active,#content .contact-left form input[type="submit"],.filter a,.skt-parallax-button,#convac-paginate a:hover,#convac-paginate .convac-current,form.wpcf7-form input[type="text"]:focus,form.wpcf7-form input[type="email"]:focus,
	form.wpcf7-form input[type="url"]:focus,form.wpcf7-form input[type="tel"]:focus,
	form.wpcf7-form input[type="number"]:focus,form.wpcf7-form input[type="range"]:focus,
	form.wpcf7-form input[type="date"]:focus,form.wpcf7-form input[type="file"]:focus,form.wpcf7-form textarea:focus,
	#convac_lite_reservation input[type="text"]:focus,
	#convac_lite_reservation input[type="email"]:focus,#sidebar select:focus,#footer select:focus,
	#convac_lite_reservation input[type="number"]:focus,#convac_lite_reservation textarea:focus,#respond input:focus, #respond textarea:focus,
	form input[type="text"]:focus,form input[type="email"]:focus,
	form input[type="url"]:focus,form input[type="tel"]:focus,
	form input[type="number"]:focus,form input[type="range"]:focus,
	form input[type="date"]:focus,form input[type="file"]:focus,form textarea:focus,
	.skt-opening-hours-widget .opening-hours-list,.widget_tag_cloud a{border-color:<?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	.clients-items li a:hover{border-bottom-color:<?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	a:hover,.ske-footer-container ul li:hover:before,.ske-footer-container ul li:hover > a,.ske_widget ul ul li:hover:before,.ske_widget ul ul li:hover,.ske_widget ul ul li:hover a,.title a ,.skepost-meta a:hover,.post-tags a:hover,.entry-title a:hover ,.readmore a:hover,#Site-map .sitemap-rows ul li a:hover ,.childpages li a,#Site-map .sitemap-rows .title,.ske_widget a:hover,#footer .third_wrapper a:hover,.ske-title,#content .contact-left form input[type="submit"],.filter a,span.team_name, a.comment-edit-link,.mid-box-mid .mid-box:hover .iconbox-content h4,.error-txt,.skt-ctabox .skt-ctabox-content h2,a.comment-edit-link:hover,.skepost-meta i,.topbar_info i, .topbar_info .head-phone-txt {color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;text-decoration: none;}
	.single #content .title,#content .post-heading,.childpages li ,.fullwidth-heading,.comment-meta a:hover,#respond .required, .skt-opening-hours-widget .opening-hours-list li:before,.ske-title.ske-footer-title,h3#comments-title, h3#reply-title,.nav-previous,.nav-next,#comments,.full-map-box .hsearch-close:hover,#convac_lite_review .convac_lite_review_form_title,.cust-review-title,#reviewer_review_box i,.single-meta-content span,.iconbox-icon i,.customer-reviews .review-menuitem,.post.skt_menu_items .menu-item-price span,.sketch_price_table .price_in_table .value  {color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;} 

	.specialities-icon .sketch-font-convac-hot-plate-icons,.review-icon .sketch-font-convac-hot-dish-icon,.about-icon.sketch-font-convac-hot-dish-icon,.about_page_content .about_icon1 .sketch-font-convac-house-icon,.about_page_content .about_icon2 .sketch-font-convac-martini-wine-glass-icon,.icon_image_cap .sketch-font-convac-chief-cap-icon,#about_logos_block .icon_image_fog .sketch-font-convac-fork-knife-icon,.iconbox-icon a.skt-featured-icons i{color: <?php if(isset($_iconcolorpicker)){ echo $_iconcolorpicker; } else { echo '#FFB73D'; } ?>;}
	.sketch_price_table .active_best_price {background-color: <?php if(isset($_iconcolorpicker)){ echo $_iconcolorpicker; } else { echo '#FFB73D'; } ?>;}

	.single-menu-rating, .single-menu-item-price, .single-menu-item-vnveg, .single-menu-itemtype,#ske-like-dislike {  border-bottom: 1px solid <?php echo $sktgbcolor; ?>; }
	
	.fdz-map-overlay{background-image: url('<?php if($_home_map_overlayimg ){ echo $_home_map_overlayimg ; } ?>');}
	
	*::-moz-selection{background: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;color:#fff;}
	::selection {background: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;color:#fff;}
	#skenav ul ul li a:hover{background-color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;color:#fff;}
	.sticky-post { border-color: <?php if(isset($bg_color)){ echo $bg_color; } ?>;  }
	#searchform input[type="submit"]{ background: none repeat scroll 0 0 <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;  }

	.col-one .box .title, .col-two .box .title, .col-three .box .title, .col-four .box .title {color: <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?> !important;  }
	.footer-top-border {border: 2px solid <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	.front-page #wrapper{background: none repeat scroll 0 0 rgba(0, 0, 0, 0); }

	/************** HEADER PAGE BACKGROUND **********/
	
	.home .header-top-wrap,.home.front-page .header-top-wrap { background: url("<?php if( get_header_image() ) { echo get_header_image(); } else { echo get_template_directory_uri().'/images/header-static-img.jpg'; } ?>") no-repeat scroll top center transparent;-webkit-background-size: cover;-moz-background-size: cover ;-o-background-size: cover ; background-size: cover ; height: 720px; width: 100%; }
	.header-top-wrap,.page .header-top-wrap,.single .header-top-wrap,.archive .header-top-wrap,.search .header-top-wrap,.error404 .header-top-wrap { background: url("<?php if(isset($_innerpage_img) && $_innerpage_img!= Null ){ echo $_innerpage_img;} else { echo get_template_directory_uri().'/images/header-static-img.jpg'; } ?>") no-repeat scroll top center transparent;-webkit-background-size: cover;-moz-background-size: cover ;-o-background-size: cover ; background-size: cover ; height: auto; width: 100%;}
	.header-top-wrap .social_icon,.page .header-top-wrap .social_icon,.single .header-top-wrap .social_icon,.archive .header-top-wrap .social_icon,.search .header-top-wrap .social_icon,.error404 .header-top-wrap .social_icon{ display:none; }
	.home.front-page .header-top-wrap .social_icon,.home.blog .header-top-wrap .social_icon{ display:block; }

	/********************** MAIN NAVIGATION **********************/
	#skenav li a:hover,#skenav .sfHover { color: #000;}
	#skenav .sfHover a{ color: #FFFFFF;}
	#skenav ul ul li{ background: none repeat scroll 0 0 #222222; color: #FFFFFF; }
	#skenav ul ul li a:hover{background-color: <?php if(isset($bg_color)){ echo $navrgbcolor; } else { echo '#f65e13'; } ?>;color:#fff;}
	#skenav ul ul:after{border-bottom-color:<?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	#skenav ul ul ul:after{border-bottom:none;}
	#skenav ul ul,#skenav ul ul ul{border-top-color:<?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;}
	#skenav ul ul ul {	margin: 0;  }
	blockquote.sketch-quote,blockquote{margin-bottom: 27px;border-left: 8px solid <?php if(isset($bg_color)){ echo $bg_color; } else { echo '#f65e13'; } ?>;border-radius: 10px; border-right: 8px solid; border-style: solid; border-width: 1px 8px; } 

	.skehead-headernav .logo {
		height: 40px;
		width: 156px;
	}


</style>

<script type="text/javascript">
jQuery('document').ready(function(){
	jQuery('ul#menu-main').sktmobilemenu({'fwidth':'<?php echo $_moblie_menu; ?>'});
});
</script>