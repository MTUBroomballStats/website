<?php
/*
 Header Author Slider
*/

$author_email = get_the_author_meta( 'ID' );
$authImageSet = get_avatar( $author_email  ,200 );
if ( get_theme_mod('_author_img', '') != '' ) {
	$authImageSet = '<img src="'.esc_url( get_theme_mod('_author_img') ).'" alt="" />';
}

$authName = get_theme_mod('_author_name', __('ALEXENDRA', 'convac-lite') );
$authDesp = get_theme_mod('_author_desp', __('Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor.','convac-lite') );

?>
<div class="container">
	<div class="row-fluid">
		<div id="author-slider" class="">
			<ul class="slides clearfix">
				<li>
					<p class="flex-caption">
						<?php echo $authImageSet; ?>
						<span class="slider-title"><?php if($authName) { echo $authName; } ?></span>
						<?php if($authDesp) { ?><span class="text"><?php echo $authDesp; ?></span><?php } ?>
					</p>
				</li>
			</ul>
			<!-- .slides -->
		</div>
		<!-- #author-slider ends -->
	</div>
	<!-- .row-fluid ends -->
</div>
<!-- .container ends -->