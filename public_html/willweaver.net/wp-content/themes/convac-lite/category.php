<?php 
/**
* The template for displaying Category pages.
* Learn more: http://codex.wordpress.org/Template_Hierarchy
*/

get_header(); ?>
<?php global $convac_lite_shortname; ?>

<div class="main-wrapper-item">
	<div class="bread-title-holder">
		<div class="bread-title-bg-image full-bg-breadimage-fixed"></div>
		<div class="container">
			<div class="row-fluid">
				<div class="container_inner clearfix">
					<h1 class="title">
						<?php printf( __( 'Category Archives : %s', 'convac-lite' ), '<span>' . single_cat_title( '', false ) . '</span>' );?> 	
					</h1>
					<?php if ((class_exists('convac_lite_breadcrumb_class'))) {$convac_lite_breadcumb->convac_lite_custom_breadcrumb();} ?>
				</div>
			</div>
		</div>
	</div>

    <div class="page-content">
		<div class="container post-wrap"> 
			<div class="row-fluid">
				<div id="container" class="span8">
					<div id="content">
						<?php if(have_posts()) : ?>
						<?php while(have_posts()) : the_post(); ?>
						<?php get_template_part( 'content', get_post_format() ); ?>
						<?php endwhile; ?>
						<?php
							$prev_link = get_previous_posts_link('&larr;Previous');
							$next_link = get_next_posts_link('Next&rarr;');
							if($prev_link || $next_link){
							?>
							<div class="navigation blog-navigation">
								<?php  if (function_exists("convac_lite_paginate") && get_theme_mod('_show_pagination', 'on') == 'on' ) { convac_lite_paginate(); } else { ?>
								<div class="alignleft"><?php previous_posts_link(__('&larr;Previous','convac-lite')) ?></div>
								<div class="alignright"><?php next_posts_link(__('Next&rarr;','convac-lite'),'') ?></div>
								<?php } ?>
							</div>
							<?php
							}
						?> 
						<?php else :  ?>
						<?php get_template_part( 'content', 'none' ); ?>
						<?php endif; ?>
					</div>
					<!-- content --> 
				</div>
				<!-- container --> 
				
				<!-- Sidebar -->
				<div id="sidebar" class="span4">
					<?php get_sidebar(); ?>
				</div>
				<!-- Sidebar --> 

			</div>
		</div>
	</div>
</div>
<?php get_footer(); ?>