<?php
/**
* The template for displaying the footer.
*
* Contains footer content and the closing of the
* #main and #page div elements.
*
*/
global $convac_lite_shortname;
?>

	<div class="clearfix"></div>
</div>
<!-- #main --> 

<!-- Footer Strip Starts Here -->
	<div id="footer_strip"></div>
<!-- Footer Strip Ends Here -->

<!-- #footer -->
<div id="footer">
	<div class="container">
		<div class="row-fluid">
			<div class="second_wrapper">
				<?php dynamic_sidebar( 'Footer Sidebar' ); ?>
				<div class="clearfix"></div>
			</div><!-- second_wrapper -->
		</div>
	</div>

	<div class="third_wrapper">
		<div class="container">
			<div class="row-fluid">
				<div class="copyright span12"> <?php echo wp_kses_post( get_theme_mod('_copyright', __('Copyright... Powered by WordPress', 'convac-lite') ) ); ?> </div>
				<div class="owner span12"><?php _e('Convac Theme by','convac-lite'); ?> <a href="<?php echo esc_url('https://sketchthemes.com/'); ?>" target="_blank"><?php _e('SketchThemes','convac-lite'); ?></a></div>
				<div class="clearfix"></div>
			</div>
		</div>
	</div><!-- third_wrapper --> 
</div>
<!-- #footer -->

</div>
<!-- #wrapper -->
	<a href="JavaScript:void(0);" title="<?php _e('Back To Top', 'convac-lite'); ?>" id="backtop"></a>
	<?php wp_footer(); ?>
</body>
</html>